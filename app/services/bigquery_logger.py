"""
BigQuery logging service.
Logs every query with full pipeline outputs — detections,
habitat, sources, latency — for dissertation evaluation and
passive wildlife monitoring.
"""

import uuid
import time
import logging
from datetime import datetime, timezone
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

PROJECT_ID = "dissertation-498512"
DATASET_ID = "wildlife_queries"
TABLE_ID   = "query_logs"
TABLE_REF  = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

_client = None


def bq_client():
    global _client
    if _client is None:
        _client = bigquery.Client(project=PROJECT_ID)
    return _client


def _parse_source(source_str: str) -> dict:
    """
    Parse source string like:
    '- IUCN Red List 2023 [https://www.iucnredlist.org] (recorded: 2024-01-01)'
    into {source_name, source_url}.
    """
    try:
        name = source_str.split("[")[0].replace("-", "").strip()
        url  = source_str.split("[")[1].split("]")[0].strip() \
               if "[" in source_str else ""
        return {"source_name": name, "source_url": url}
    except Exception:
        return {"source_name": source_str[:200], "source_url": ""}


def log_query(pipeline_result: dict, latency_ms: float) -> bool:
    """
    Insert one row into BigQuery with the full pipeline output.

    Args:
        pipeline_result : dict returned by run_pipeline()
        latency_ms      : end-to-end request latency in milliseconds

    Returns True on success, False on failure (non-blocking).
    """
    try:
        detections = pipeline_result.get("detections", [])
        habitat    = pipeline_result.get("habitat", {})
        sources    = pipeline_result.get("sources", [])

        # Build detection records
        det_records = []
        for d in detections:
            top3 = d.get("top3", [])
            det_records.append({
                "species"     : d.get("species", ""),
                "species_conf": d.get("species_conf", 0.0),
                "yolo_label"  : d.get("yolo_label", ""),
                "yolo_conf"   : d.get("yolo_conf", 0.0),
                "top1_species": top3[0]["species"] if len(top3) > 0 else "",
                "top2_species": top3[1]["species"] if len(top3) > 1 else "",
                "top3_species": top3[2]["species"] if len(top3) > 2 else "",
            })

        # Build source records
        src_records = [_parse_source(s) for s in sources]

        row = {
            "query_id"        : str(uuid.uuid4()),
            "timestamp"       : datetime.now(timezone.utc).isoformat(),
            "question"        : pipeline_result.get("question", ""),
            "answer"          : pipeline_result.get("answer", ""),
            "num_animals"     : pipeline_result.get("num_animals", 0),
            "habitat"         : habitat.get("habitat", ""),
            "time_of_day"     : habitat.get("time_of_day", ""),
            "vegetation_ratio": habitat.get("vegetation_ratio", 0.0),
            "water_ratio"     : habitat.get("water_ratio", 0.0),
            "brightness"      : habitat.get("brightness", 0.0),
            "sources_used"    : pipeline_result.get("sources_used", 0),
            "latency_ms"      : round(latency_ms, 2),
            "yolo_fallback"   : any(
                d.get("yolo_label") == "full_image_fallback"
                for d in detections
            ),
            "detections"      : det_records,
            "sources"         : src_records,
        }

        errors = bq_client().insert_rows_json(TABLE_REF, [row])
        if errors:
            logger.error(f"BigQuery insert errors: {errors}")
            return False

        logger.info(f"Logged query [{row['query_id'][:8]}] to BigQuery")
        return True

    except GoogleAPIError as e:
        logger.error(f"BigQuery API error: {e}")
        return False
    except Exception as e:
        logger.error(f"BigQuery logging failed: {e}")
        return False
