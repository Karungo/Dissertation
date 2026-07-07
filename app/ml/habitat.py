import logging
import cv2
import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from core.config import SEED

logger = logging.getLogger(__name__)


def analyse_habitat(image: Image.Image, n_colours: int = 5) -> dict:
    """
    OpenCV computer vision scene analysis:
    - HSV segmentation  → vegetation / water / dry grass ratios
    - KMeans            → dominant colour palette
    - Brightness        → time of day estimate
    - Edge density      → scene complexity
    Returns structured dict used to enrich the RAG prompt.
    """
    img_rgb = np.array(image.convert("RGB"))
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, w    = img_rgb.shape[:2]

    # Dominant colours
    pixels  = img_rgb.reshape(-1, 3).astype(np.float32)
    km      = KMeans(n_clusters=n_colours, random_state=SEED, n_init=5)
    km.fit(pixels)

    # HSV ratios
    veg   = cv2.inRange(img_hsv, (35,40,40),  (85,255,255))
    water = cv2.inRange(img_hsv, (100,40,40), (130,255,255))
    dry   = cv2.inRange(img_hsv, (20,30,100), (35,200,255))

    veg_r   = float(veg.sum()   / (255 * h * w))
    water_r = float(water.sum() / (255 * h * w))
    dry_r   = float(dry.sum()   / (255 * h * w))

    gray       = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    brightness = float(gray.mean())
    edges      = cv2.Canny(gray, 50, 150)
    edge_den   = float(edges.sum() / (255 * h * w))

    # Time of day
    if   brightness < 50:  tod = "night"
    elif brightness < 100: tod = "dawn / dusk"
    elif brightness < 170: tod = "morning / afternoon"
    else:                  tod = "midday"

    # Habitat
    if   water_r > 0.15:  habitat = "riverine / water"
    elif veg_r   > 0.35:  habitat = "bush / woodland"
    elif dry_r   > 0.30:  habitat = "open savannah"
    elif edge_den > 0.15: habitat = "rocky / dense bush"
    else:                 habitat = "open grassland"

    return {
        "habitat"          : habitat,
        "vegetation_ratio" : round(veg_r,    3),
        "water_ratio"      : round(water_r,  3),
        "dry_ratio"        : round(dry_r,    3),
        "brightness"       : round(brightness, 1),
        "time_of_day"      : tod,
        "edge_density"     : round(edge_den, 3),
    }
