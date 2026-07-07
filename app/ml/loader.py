import logging
import tensorflow as tf
from core.config import BUCKET_NAME, MODEL_BLOB, LOCAL_MODEL
from services.storage import download_if_missing

logger  = logging.getLogger(__name__)
_model  = None

def load_model():
    global _model
    if _model is not None:
        return _model
    download_if_missing(BUCKET_NAME, MODEL_BLOB, LOCAL_MODEL)
    logger.info("Loading CNN model ...")
    _model = tf.keras.models.load_model(LOCAL_MODEL)
    logger.info("CNN model loaded ✓")
    return _model
