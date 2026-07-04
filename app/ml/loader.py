import logging
import tensorflow as tf
from core.config import BUCKET_NAME, MODEL_BLOB, LOCAL_MODEL_PATH
from services.storage import download_if_missing

logger = logging.getLogger(__name__)

_model = None

def load_model():
    """
    Load the EfficientNet-B4 Keras model.
    Downloads from GCS on first call, then caches in memory.
    """
    global _model

    if _model is not None:
        return _model

    # Download from GCS if not already cached locally
    download_if_missing(BUCKET_NAME, MODEL_BLOB, LOCAL_MODEL_PATH)

    logger.info(f"Loading Keras model from {LOCAL_MODEL_PATH} ...")
    _model = tf.keras.models.load_model(LOCAL_MODEL_PATH)
    logger.info("CNN model loaded successfully.")
    return _model
