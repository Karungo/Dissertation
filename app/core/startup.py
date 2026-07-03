from services.storage import download_if_missing
from core.config import *

def startup():
    # model
    download_if_missing(BUCKET_NAME, MODEL_BLOB, MODEL_PATH)

    # vectorstore
    download_if_missing(BUCKET_NAME, FAISS_INDEX_BLOB, f"{VECTOR_DIR}/index.faiss")
    download_if_missing(BUCKET_NAME, FAISS_META_BLOB, f"{VECTOR_DIR}/index.pkl")
