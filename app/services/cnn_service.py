import json
import numpy as np
import tensorflow as tf

from PIL import Image

from services.model_loader import (
    load_model
)
with open(
    "models/class_names.json",
    "r"
) as f:

    CLASS_NAMES = json.load(f)

IMG_SIZE = 380


def preprocess(image):

    image = image.resize(
        (IMG_SIZE, IMG_SIZE)
    )

    arr = np.array(image)

    arr = tf.keras.applications.efficientnet.preprocess_input(
        arr
    )

    return np.expand_dims(
        arr,
        axis=0
    )

def predict_species(
    image,
    top_k=3
):

    model = load_model()

    arr = preprocess(image)

    preds = model.predict(
        arr,
        verbose=0
    )[0]

    indices = np.argsort(
        preds
    )[::-1][:top_k]

    results = []

    for idx in indices:

        results.append({
            "species":
                CLASS_NAMES[idx],

            "confidence":
                float(preds[idx])
        })

    return results
