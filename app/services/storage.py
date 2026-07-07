import os
import logging
from pathlib import Path
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

_client = None

def gcs_client():
    global _client
    if _client is None:
        _client = storage.Client()
    return _client


def download_if_missing(bucket_name: str, blob_name: str, local_path: str) -> str:
    if Path(local_path).exists():
        logger.info(f"Cached: {local_path}")
        return local_path
    Path(local_path).parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Downloading gs://{bucket_name}/{blob_name} → {local_path}")
    try:
        gcs_client().bucket(bucket_name).blob(blob_name).download_to_filename(local_path)
        logger.info(f"Download complete: {local_path}")
    except GoogleAPIError as e:
        logger.error(f"GCS download failed [{blob_name}]: {e}")
        raise
    return local_path
