import os
import logging
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from core.config import (
    BUCKET_NAME, FAISS_INDEX_BLOB, FAISS_PKL_BLOB,
    LOCAL_VS_DIR, EMBEDDING_MODEL
)
from services.storage import download_if_missing

logger      = logging.getLogger(__name__)
_vectorstore = None
_embeddings  = None


def load_vectorstore():
    global _vectorstore, _embeddings
    if _vectorstore is not None:
        return _vectorstore

    os.makedirs(LOCAL_VS_DIR, exist_ok=True)

    download_if_missing(
        BUCKET_NAME, FAISS_INDEX_BLOB,
        os.path.join(LOCAL_VS_DIR, "index.faiss")
    )
    download_if_missing(
        BUCKET_NAME, FAISS_PKL_BLOB,
        os.path.join(LOCAL_VS_DIR, "index.pkl")
    )

    logger.info(f"Loading embedding model ({EMBEDDING_MODEL}) ...")
    _embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    logger.info("Loading FAISS index ...")
    _vectorstore = FAISS.load_local(
        LOCAL_VS_DIR, _embeddings,
        allow_dangerous_deserialization=True
    )
    logger.info("Vectorstore loaded ✓")
    return _vectorstore
