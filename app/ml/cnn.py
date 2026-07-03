import numpy as np
import json
import tensorflow as tf
from PIL import Image

from core.config import CLASS_NAMES_PATH
from ml.loader import get_model

with open(CLASS_NAMES_PATH, "r") as f:
    CLASS_NAMES = json.load(f)

IMG_SIZE = 224


def preprocess(image):
    image = image.resize((IMG_SIZE, IMG_SIZE))
    arr = np.array(image)

    arr = tf.keras.applications.efficientnet.preprocess_input(arr)

    return np.expand_dims(arr, axis=0)


def predict_species(image, top_k=3):
    model = get_model()
    arr = preprocess(image)

    preds = model.predict(arr, verbose=0)[0]

    indices = np.argsort(preds)[::-1][:top_k]

    return [
        {
            "species": CLASS_NAMES[i],
            "confidence": float(preds[i])
        }
        for i in indices
    ]
