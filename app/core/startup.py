import logging
from ml.loader import load_model
from ml.yolo_detector import load_yolo
from rag.vectorstore import load_vectorstore

logger = logging.getLogger(__name__)


def startup():
    logger.info("=== Starting Maasai Mara Wildlife API ===")

    try:
        load_model()
    except Exception as e:
        logger.critical(f"CNN model failed to load: {e}")
        raise RuntimeError(f"Startup failed — CNN: {e}") from e

    try:
        load_yolo()
    except Exception as e:
        logger.critical(f"YOLOv8 failed to load: {e}")
        raise RuntimeError(f"Startup failed — YOLOv8: {e}") from e

    try:
        load_vectorstore()
    except Exception as e:
        logger.critical(f"Vectorstore failed to load: {e}")
        raise RuntimeError(f"Startup failed — vectorstore: {e}") from e

    logger.info("=== All components loaded. API ready. ===")
