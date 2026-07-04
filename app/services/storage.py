import os
import logging
from google.cloud import storage
from google.api_core.exceptions import GoogleAPIError

logger = logging.getLogger(__name__)

_client = None

def get_client():
    global _client
    if _client is None:
        _client = storage.Client()
    return _client

def download_if_missing(bucket_name: str, blob_path: str, local_path: str) -> str:
    """
    Download a file from GCS only if it does not already exist locally.
    Returns the local path on success. Raises on failure.
    """
    if os.path.exists(local_path):
        logger.info(f"Using cached file: {local_path}")
        return local_path

    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    logger.info(f"Downloading gs://{bucket_name}/{blob_path} → {local_path}")

    try:
        client = get_client()
        bucket = client.bucket(bucket_name)
        blob   = bucket.blob(blob_path)
        blob.download_to_filename(local_path)
        logger.info(f"Download complete: {local_path}")
    except GoogleAPIError as e:
        logger.error(f"GCS download failed for {blob_path}: {e}")
        raise

    return local_path
