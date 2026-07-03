import json
import numpy as np
import tensorflow as tf

from PIL import Image

from ml.loader import load_model

IMG_SIZE = 224

with open("models/class_names.json") as f:
    CLASS_NAMES = json.load(f)


def preprocess(image):

    image = image.resize((IMG_SIZE, IMG_SIZE))

    arr = np.array(image)

    arr = tf.keras.applications.efficientnet.preprocess_input(arr)

    return np.expand_dims(arr, 0)


def predict_species(image, top_k=3):

    model = load_model()

    preds = model.predict(
        preprocess(image),
        verbose=0
    )[0]

    indices = np.argsort(preds)[::-1][:top_k]

    return [
        {
            "species": CLASS_NAMES[i],
            "confidence": float(preds[i])
        }
        for i in indices
    ]
