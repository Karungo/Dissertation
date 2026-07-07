import os
import logging

logger = logging.getLogger(__name__)

# ── GCS ──────────────────────────────────────────────────────────────────────
BUCKET_NAME       = os.getenv("BUCKET_NAME", "animals-dataset-dissertation")
MODEL_BLOB        = "models/maasai_mara_efficientnet_b4.keras"
META_BLOB         = "models/animal_classifier_metadata.json"
FAISS_INDEX_BLOB  = "vectorstore/index.faiss"
FAISS_PKL_BLOB    = "vectorstore/index.pkl"

# ── Local paths ───────────────────────────────────────────────────────────────
LOCAL_MODEL       = "/tmp/models/maasai_mara_efficientnet_b4.keras"
LOCAL_META        = "/tmp/models/animal_classifier_metadata.json"
LOCAL_VS_DIR      = "/tmp/vectorstore"

# ── Model ─────────────────────────────────────────────────────────────────────
IMG_SIZE          = 224
TOP_K             = 3
YOLO_CONF         = 0.25
SEED              = 42

# ── Embedding ─────────────────────────────────────────────────────────────────
EMBEDDING_MODEL   = "sentence-transformers/all-mpnet-base-v2"

# ── Gemini ────────────────────────────────────────────────────────────────────
GEMINI_API_KEY    = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL      = "gemini-2.5-flash"

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is not set."
    )

os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
