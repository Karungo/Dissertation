import os
import tensorflow as tf
from config import MODEL_BLOB

model = None


def load_model():
    global model

    # If already loaded in memory, reuse it
    if model is not None:
        return model

    # Ensure model exists locally
    if not os.path.exists(MODEL_BLOB):
        raise FileNotFoundError(
            f"Model file not found at {MODEL_BLOB}. "
            "Please ensure the model is downloaded or included in the repo."
        )

    # Load model once
    model = tf.keras.models.load_model(MODEL_BLOB)

    return model
