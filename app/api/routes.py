import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.pipeline import analyze_image

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze")
async def analyze(
    image   : UploadFile = File(..., description="Wildlife image"),
    question: str        = Form(..., description="Natural language question about the animal")
):
    """
    Identify the species in an uploaded image and answer a tourist's question
    using the CNN + RAG pipeline.
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = await analyze_image(image, question)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unhandled error in /analyze: {e}")
        raise HTTPException(status_code=500, detail="Internal server error. Please try again.")
