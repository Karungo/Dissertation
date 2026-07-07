import logging
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from services.pipeline import run_pipeline

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/analyze")
async def analyze(
    image   : UploadFile = File(..., description="Wildlife image"),
    question: str        = Form(..., description="Natural language question")
):
    """
    Main endpoint — upload a wildlife image and ask a question.
    Returns species detections, habitat analysis, and a grounded RAG answer.
    """
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    if not question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        result = await run_pipeline(image, question)
        return result
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"/analyze error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")
