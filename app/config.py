import os

PROJECT_ID = os.getenv("PROJECT_ID")

BUCKET_NAME = os.getenv(
    "BUCKET_NAME",
    "wildlife-rag-storage"
)

MODEL_BLOB = (
    "models/maasai_mara_efficientnet_b4.keras"
)

FAISS_INDEX_BLOB = (
    "vectorstore/index.faiss"
)

FAISS_META_BLOB = (
    "vectorstore/index.pkl"
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

TOP_K = 3

CONFIDENCE_THRESHOLD = 0.60
