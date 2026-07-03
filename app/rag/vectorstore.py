import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from google.cloud import storage

from core.config import (
    BUCKET_NAME,
    FAISS_INDEX_BLOB,
    FAISS_META_BLOB
)

VECTOR_DIR = "/tmp/vectorstore"
vectorstore = None

client = storage.Client()

def download_blob(bucket, blob_name, destination):
    b = client.bucket(bucket)
    blob = b.blob(blob_name)
    blob.download_to_filename(destination)

def load_vectorstore():
    global vectorstore

    if vectorstore is not None:
        return vectorstore

    os.makedirs(VECTOR_DIR, exist_ok=True)

    index_path = f"{VECTOR_DIR}/index.faiss"
    meta_path = f"{VECTOR_DIR}/index.pkl"

    if not os.path.exists(index_path):
        download_blob(BUCKET_NAME, FAISS_INDEX_BLOB, index_path)
        download_blob(BUCKET_NAME, FAISS_META_BLOB, meta_path)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vectorstore
