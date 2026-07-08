import io
import time
import logging
from PIL import Image
from ml.yolo_detector import detect_and_classify
from ml.cnn import classify_full_image
from ml.habitat import analyse_habitat
from rag.retrieval import retrieve_context
from llm.gemini import generate_answer
from services.bigquery_logger import log_query

logger = logging.getLogger(__name__)


async def run_pipeline(upload_file, question: str) -> dict:
    """
    Full end-to-end pipeline with BigQuery logging:
    1. Read image
    2. YOLOv8 detect + EfficientNet-B4 classify per crop
    3. OpenCV habitat analysis
    4. FAISS retrieve KB chunks per detected species
    5. Gemini generate grounded answer with source citations
    6. Log full result to BigQuery (non-blocking)
    """
    start = time.time()

    # ── Step 1: Read image ────────────────────────────────────────────────
    raw   = await upload_file.read()
    image = Image.open(io.BytesIO(raw)).convert("RGB")

    # ── Step 2: Detection + classification ────────────────────────────────
    detections = detect_and_classify(image)

    if not detections:
        logger.warning("YOLOv8 found nothing — running CNN on full image")
        preds = classify_full_image(image)
        detections = [{
            "bbox"        : None,
            "yolo_label"  : "full_image_fallback",
            "yolo_conf"   : 1.0,
            "species"     : preds[0]["species"],
            "species_conf": preds[0]["confidence"],
            "top3"        : preds,
        }]

    # ── Step 3: Habitat ───────────────────────────────────────────────────
    habitat = analyse_habitat(image)

    # ── Step 4: Retrieve — all species, deduplicated ──────────────────────
    seen_content, all_docs = set(), []
    for det in detections:
        for doc in retrieve_context(det["species"], question):
            if doc.page_content not in seen_content:
                seen_content.add(doc.page_content)
                all_docs.append(doc)

    context = "\n\n".join(d.page_content for d in all_docs)

    seen_src, sources = set(), []
    for doc in all_docs:
        m   = doc.metadata
        key = m.get("source", "")
        if key and key not in seen_src:
            seen_src.add(key)
            sources.append(
                f"- {m.get('source','')} "
                f"[{m.get('source_url','')}] "
                f"(recorded: {m.get('date_recorded','')})"
            )

    # ── Step 5: Generate ──────────────────────────────────────────────────
    answer = generate_answer(detections, habitat, context, sources, question)

    latency_ms = (time.time() - start) * 1000

    result = {
        "num_animals" : len(detections),
        "detections"  : detections,
        "habitat"     : habitat,
        "question"    : question,
        "answer"      : answer,
        "sources_used": len(all_docs),
        "sources"     : sources,
        "latency_ms"  : round(latency_ms, 2),
    }

    # ── Step 6: Log to BigQuery (non-blocking — never fails the request) ──
    log_query(result, latency_ms)

    return result
