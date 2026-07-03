import threading

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

vectorstore = None


def load_vectorstore():
    global vectorstore

    if vectorstore is not None:
        return vectorstore

    ...
    vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True,
    )

    return vectorstore
