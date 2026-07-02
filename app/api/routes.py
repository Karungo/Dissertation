from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form
from services.pipeline import analyze_image

router = APIRouter()


@router.post("/analyze")
async def analyze(
    image: UploadFile = File(...),
    question: str = Form(...)
):

    result = await analyze_image(
        image,
        question
    )

    return result
