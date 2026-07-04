import os
import logging

logger = logging.getLogger(__name__)

BUCKET_NAME      = os.getenv("BUCKET_NAME", "animals-dataset-dissertation")

MODEL_BLOB       = "models/maasai_mara_efficientnet_b4.keras"
LOCAL_MODEL_PATH = "/tmp/models/maasai_mara_efficientnet_b4.keras"

FAISS_INDEX_BLOB = "vectorstore/index.faiss"
FAISS_META_BLOB  = "vectorstore/index.pkl"
VECTOR_DIR       = "/tmp/vectorstore"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set. "
        "Set it before starting the server."
    )

TOP_K                = 3
CONFIDENCE_THRESHOLD = 0.60
