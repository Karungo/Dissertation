from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from core.config import VECTOR_DIR

_vectorstore = None

def get_vectorstore():
    global _vectorstore

    if _vectorstore:
        return _vectorstore

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )

    _vectorstore = FAISS.load_local(
        VECTOR_DIR,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return _vectorstore
