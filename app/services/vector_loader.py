import os

from langchain_community.vectorstores import FAISS

from langchain_google_genai import (
    GoogleGenerativeAIEmbeddings
)

from services.gcs_loader import (
    download_blob
)

from config import (
    BUCKET_NAME,
    FAISS_INDEX_BLOB,
    FAISS_META_BLOB
)

VECTOR_DIR = "/tmp/vectorstore"

vectorstore = None
