import logging
import cv2
import numpy as np
from PIL import Image
from ultralytics import YOLO
from ml.cnn import classify_crop
from core.config import YOLO_CONF

logger = logging.getLogger(__name__)

_yolo = None

# COCO classes present in Maasai Mara — used for labelling only.
# No classes= filter applied so YOLO detects ALL animals generically.
COCO_MARA = {16: "bird", 22: "elephant", 24: "zebra", 25: "giraffe"}


def load_yolo():
    global _yolo
    if _yolo is None:
        logger.info("Loading YOLOv8n ...")
        _yolo = YOLO("yolov8n.pt")
        logger.info("YOLOv8n loaded ✓")
    return _yolo


def detect_and_classify(image: Image.Image, conf: float = YOLO_CONF) -> list[dict]:
    """
    YOLOv8 detects all animals (no COCO class filter) →
    EfficientNet-B4 classifies each crop.
    Returns list of detection dicts.
    """
    yolo    = load_yolo()
    img_rgb = np.array(image.convert("RGB"))
    results = yolo(img_rgb, conf=conf, verbose=False)
    boxes   = results[0].boxes
    detections = []

    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
        yolo_conf  = float(box.conf[0])
        yolo_label = COCO_MARA.get(int(box.cls[0]), "animal")

        crop = img_rgb[max(0,y1):max(0,y2), max(0,x1):max(0,x2)]
        if crop.size == 0:
            continue

        preds = classify_crop(crop)
        detections.append({
            "bbox"        : [x1, y1, x2, y2],
            "yolo_label"  : yolo_label,
            "yolo_conf"   : round(yolo_conf, 4),
            "species"     : preds[0]["species"],
            "species_conf": preds[0]["confidence"],
            "top3"        : preds,
        })

    logger.info(f"YOLOv8 detected {len(detections)} animal(s)")
    return detections
