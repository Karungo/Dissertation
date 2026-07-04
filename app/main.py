import logging
from fastapi import FastAPI
from api.routes import router
from core.startup import startup
from ml.loader import load_model
from rag.vectorstore import load_vectorstore

# Configure logging for the whole application
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI(
    title="Maasai Mara Wildlife API",
    description="CNN + RAG wildlife identification and Q&A system for Maasai Mara tourists.",
    version="1.0"
)


@app.on_event("startup")
def on_startup():
    startup()


app.include_router(router)


@app.get("/health")
def health():
    """
    Health check that reflects the actual state of loaded components.
    Returns 503 if either the CNN model or vectorstore failed to load.
    """
    from fastapi.responses import JSONResponse

    cnn_ok = load_model() is not None
    vs_ok  = load_vectorstore() is not None

    status = "ok" if (cnn_ok and vs_ok) else "degraded"
    code   = 200 if status == "ok" else 503

    return JSONResponse(
        status_code=code,
        content={
            "status"     : status,
            "cnn_loaded" : cnn_ok,
            "rag_loaded" : vs_ok
        }
    )
