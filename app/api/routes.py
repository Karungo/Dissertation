from fastapi import APIRouter, UploadFile, File, Form

from services.pipeline import analyze_image

router = APIRouter(tags=["Wildlife"])


@router.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    return await analyze_image(image, question)
