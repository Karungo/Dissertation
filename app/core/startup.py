from ml.loader import load_model
from rag.vectorstore import load_vectorstore

def startup():
    # preload heavy stuff ONCE
    load_model()
    load_vectorstore()
