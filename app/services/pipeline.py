import logging
from PIL import Image
from ml.cnn import predict_species
from rag.retrieval import retrieve_context
from llm.gemini import generate_answer

logger = logging.getLogger(__name__)


async def analyze_image(upload_file, question: str) -> dict:
    """
    Full end-to-end pipeline:
    1. Read and validate the uploaded image
    2. Run CNN species identification
    3. Retrieve relevant knowledge base documents (deduplicated)
    4. Generate a grounded answer with Gemini
    """
    # Step 1: Read image
    try:
        image = Image.open(upload_file.file).convert("RGB")
    except Exception as e:
        logger.error(f"Failed to read uploaded image: {e}")
        raise ValueError(f"Could not open image: {e}")

    # Step 2: CNN prediction
    predictions = predict_species(image)

    # Step 3: Retrieve context — deduplicate across all predictions
    seen = set()
    docs = []
    for p in predictions:
        for doc in retrieve_context(p["species"], question):
            if doc.page_content not in seen:
                seen.add(doc.page_content)
                docs.append(doc)

    logger.info(f"Total unique docs retrieved: {len(docs)}")

    # Step 4: Generate answer
    answer = generate_answer(question, predictions, docs)

    return {
        "predictions": predictions,
        "answer"     : answer
    }
