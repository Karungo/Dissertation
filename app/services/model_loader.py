import os
import tensorflow as tf

from config import (
    BUCKET_NAME,
    MODEL_BLOB
)

from services.gcs_loader import (
    download_blob
)

LOCAL_MODEL = "/tmp/model.keras"

model = None


def load_model():

    global model

    if model is not None:
        return model

    if not os.path.exists(
        LOCAL_MODEL
    ):

        download_blob(
            BUCKET_NAME,
            MODEL_BLOB,
            LOCAL_MODEL
        )

    model = tf.keras.models.load_model(
        LOCAL_MODEL
    )

    return model
