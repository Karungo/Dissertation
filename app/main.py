from fastapi import FastAPI
from api.routes import router
from core.startup import startup

app = FastAPI()

@app.on_event("startup")
def on_startup():
    startup()

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok"}
