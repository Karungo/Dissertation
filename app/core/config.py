import os

BUCKET_NAME = os.getenv("BUCKET_NAME", "animals-dataset-dissertation")

MODEL_PATH = "/tmp/models/model.keras"
CLASS_NAMES_PATH = "/tmp/models/class_names.json"

VECTOR_DIR = "/tmp/vectorstore"

FAISS_INDEX_BLOB = "vectorstore/index.faiss"
FAISS_META_BLOB = "vectorstore/index.pkl"

MODEL_BLOB = "models/maasai_mara_efficientnet_b4.keras"

TOP_K = 3
CONFIDENCE_THRESHOLD = 0.60

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
