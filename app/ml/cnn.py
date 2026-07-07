import os
import json
import logging
import cv2
import numpy as np
import tensorflow as tf
from PIL import Image
from ml.loader import load_model
from core.config import IMG_SIZE, TOP_K

logger = logging.getLogger(__name__)

_BASE       = os.path.dirname(os.path.abspath(__file__))
_META_PATH  = os.path.join(_BASE, "..", "models", "class_names.json")

# Loaded at import time — safe because startup() validates the file exists
with open(_META_PATH) as f:
    _meta = json.load(f)

CLASS_TO_INDEX = _meta["class_to_index"]
IDX_TO_CLASS   = {int(v): k for k, v in CLASS_TO_INDEX.items()}
NUM_CLASSES    = len(IDX_TO_CLASS)
logger.info(f"Loaded {NUM_CLASSES} class names")


def classify_crop(crop_rgb: np.ndarray) -> list[dict]:
    """Run EfficientNet-B4 on an RGB numpy crop. Returns top-k predictions."""
    model   = load_model()
    resized = cv2.resize(crop_rgb, (IMG_SIZE, IMG_SIZE)).astype(np.float32)
    tensor  = tf.keras.applications.efficientnet.preprocess_input(resized)
    tensor  = np.expand_dims(tensor, 0)
    probs   = model.predict(tensor, verbose=0)[0]
    top_idx = np.argsort(probs)[::-1][:TOP_K]
    return [
        {"species": IDX_TO_CLASS[int(i)], "confidence": round(float(probs[i]), 4)}
        for i in top_idx
    ]


def classify_full_image(image: Image.Image) -> list[dict]:
    """Run EfficientNet-B4 on a full PIL Image. Used as YOLO fallback."""
    model   = load_model()
    img     = image.convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    arr     = np.array(img, dtype=np.float32)
    arr     = tf.keras.applications.efficientnet.preprocess_input(arr)
    arr     = np.expand_dims(arr, 0)
    probs   = model.predict(arr, verbose=0)[0]
    top_idx = np.argsort(probs)[::-1][:TOP_K]
    return [
        {"species": IDX_TO_CLASS[int(i)], "confidence": round(float(probs[i]), 4)}
        for i in top_idx
    ]
