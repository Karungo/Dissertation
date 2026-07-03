import os
import tensorflow as tf

from config import MODEL_BLOB

model = None


def load_model():
    global model

    if model is not None:
        return model

    if not os.path.exists(MODEL_BLOB):
        raise FileNotFoundError(MODEL_BLOB)

    model = tf.keras.models.load_model(MODEL_BLOB)

    return model
