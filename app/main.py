import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from api.routes import router
from core.startup import startup
from ml.loader import load_model
from rag.vectorstore import load_vectorstore
from ml.yolo_detector import load_yolo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

app = FastAPI(
    title="Maasai Mara Wildlife API",
    description=(
        "Intelligent wildlife query system for Maasai Mara tourists. "
        "YOLOv8 multi-animal detection + EfficientNet-B4 species classification "
        "+ OpenCV habitat analysis + Gemini RAG grounded answers."
    ),
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    startup()


app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Maasai Mara Wildlife API",
        "version": "2.0.0",
        "docs"   : "/docs",
        "health" : "/health"
    }


@app.get("/health")
def health():
    """Real health check — verifies all components are loaded."""
    try:
        cnn_ok  = load_model()    is not None
        vs_ok   = load_vectorstore() is not None
        yolo_ok = load_yolo()     is not None
    except Exception:
        cnn_ok = vs_ok = yolo_ok = False

    status = "ok" if all([cnn_ok, vs_ok, yolo_ok]) else "degraded"
    return JSONResponse(
        status_code=200 if status == "ok" else 503,
        content={
            "status"     : status,
            "cnn_loaded" : cnn_ok,
            "rag_loaded" : vs_ok,
            "yolo_loaded": yolo_ok,
        }
    )
