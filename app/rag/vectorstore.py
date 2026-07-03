import threading

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

_vectorstore = None
_lock = threading.Lock()


def load_vectorstore():

    global _vectorstore

    if _vectorstore is None:

        with _lock:

            if _vectorstore is None:

                embeddings = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-mpnet-base-v2"
                )

                _vectorstore = FAISS.load_local(
                    "/tmp/vectorstore",
                    embeddings,
                    allow_dangerous_deserialization=True
                )

    return _vectorstore
