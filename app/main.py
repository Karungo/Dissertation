from fastapi import FastAPI

from api.routes import router

app = FastAPI(
    title="Wildlife Identification API",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Wildlife Identification API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
