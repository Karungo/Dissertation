from fastapi import FastAPI
from api.routes import router
from core.startup import lifespan

app = FastAPI(
    title="Wildlife Identification API",
    version="1.0",
    lifespan=lifespan
)

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "healthy"}
