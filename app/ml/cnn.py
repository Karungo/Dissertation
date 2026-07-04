import os
import json
import logging
import numpy as np
import tensorflow as tf
from PIL import Image
from ml.loader import load_model

logger  = logging.getLogger(__name__)
IMG_SIZE = 224  # Model was trained at 224x224

# Load class names using an absolute path so it works regardless of
# the working directory uvicorn is launched from
_BASE       = os.path.dirname(os.path.abspath(__file__))
_CLASS_PATH = os.path.join(_BASE, "..", "models", "class_names.json")

with open(_CLASS_PATH) as f:
    CLASS_NAMES = json.load(f)

logger.info(f"Loaded {len(CLASS_NAMES)} class names.")


def preprocess(image: Image.Image) -> np.ndarray:
    """Resize and apply EfficientNet preprocessing."""
    image = image.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr   = np.array(image, dtype=np.float32)
    arr   = tf.keras.applications.efficientnet.preprocess_input(arr)
    return np.expand_dims(arr, axis=0)


def predict_species(image: Image.Image, top_k: int = 3) -> list[dict]:
    """
    Run inference and return the top-k species predictions.
    Each result is {"species": str, "confidence": float}.
    """
    model   = load_model()
    arr     = preprocess(image)
    preds   = model.predict(arr, verbose=0)[0]
    indices = np.argsort(preds)[::-1][:top_k]

    results = [
        {
            "species"   : CLASS_NAMES[i],
            "confidence": round(float(preds[i]), 4)
        }
        for i in indices
    ]
    logger.info(f"Top prediction: {results[0]['species']} ({results[0]['confidence']*100:.1f}%)")
    return results
