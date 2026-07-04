import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from core.config import (
    BUCKET_NAME,
    FAISS_INDEX_BLOB,
    FAISS_META_BLOB,
    VECTOR_DIR
)
from services.storage import download_if_missing

logger      = logging.getLogger(__name__)
_vectorstore = None


def load_vectorstore():
    """
    Load the FAISS vectorstore.
    Downloads index files from GCS on first call, then caches in memory.
    Embedding model must match the one used to build the index.
    """
    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    os.makedirs(VECTOR_DIR, exist_ok=True)

    index_path = os.path.join(VECTOR_DIR, "index.faiss")
    meta_path  = os.path.join(VECTOR_DIR, "index.pkl")

    download_if_missing(BUCKET_NAME, FAISS_INDEX_BLOB, index_path)
    download_if_missing(BUCKET_NAME, FAISS_META_BLOB,  meta_path)

    logger.info("Loading embedding model (all-mpnet-base-v2)...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    logger.info("Loading FAISS index...")
    _vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )
    logger.info("Vectorstore loaded successfully.")
    return _vectorstore
