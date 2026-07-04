import logging
from ml.loader import load_model
from rag.vectorstore import load_vectorstore

logger = logging.getLogger(__name__)


def startup():
    """
    Pre-load heavy components at server startup so the first
    request is not slow and failures are caught immediately.
    """
    logger.info("=== Starting up Maasai Mara Wildlife API ===")

    try:
        load_model()
    except Exception as e:
        logger.critical(f"CNN model failed to load: {e}")
        raise RuntimeError(f"Startup failed — CNN model: {e}") from e

    try:
        load_vectorstore()
    except Exception as e:
        logger.critical(f"Vectorstore failed to load: {e}")
        raise RuntimeError(f"Startup failed — vectorstore: {e}") from e

    logger.info("=== All components loaded. API ready. ===")
