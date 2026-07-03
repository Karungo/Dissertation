import tensorflow as tf
import threading

MODEL_PATH = "models/maasai_mara_efficientnet_b4.keras"

_model = None
_lock = threading.Lock()


def load_model():

    global _model

    if _model is None:

        with _lock:

            if _model is None:

                _model = tf.keras.models.load_model(
                    MODEL_PATH
                )

    return _model
