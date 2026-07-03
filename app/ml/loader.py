import tensorflow as tf
from core.config import MODEL_PATH

_model = None

def get_model():
    global _model

    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH)

    return _model
