import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from services.storage import download_if_missing
from core.config import (
    BUCKET_NAME,
    FAISS_INDEX_BLOB,
    FAISS_META_BLOB
)

VECTOR_DIR = "/tmp/vectorstore"

_vectorstore = None


def load_vectorstore():
    global _vectorstore

    if _vectorstore:
        return _vectorstore

    os.makedirs(VECTOR_DIR, exist_ok=True)

    index_path = f"{VECTOR_DIR}/index.faiss"
    meta_path = f"{VECTOR_DIR}/index.pkl"

    if not os.path.exists(index_path):
        download_blob(BUCKET_NAME, FAISS_INDEX_BLOB, index_path)
        download_blob(BUCKET_NAME, FAISS_META_BLOB, meta_path)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    _vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return _vectorstore
