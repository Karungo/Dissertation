import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GEMINI_API_KEY

logger = logging.getLogger(__name__)

# Initialise LLM once at module load — safe because GEMINI_API_KEY
# is validated in config.py before this import can succeed
_llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)


def generate_answer(question: str, predictions: list, docs: list) -> str:
    """
    Generate a grounded natural language answer using Gemini.
    Uses only retrieved context — does not hallucinate beyond it.
    """
    if not docs:
        logger.warning("No context documents retrieved — answer may be limited.")
        context = "No specific information available for this species."
    else:
        context = "\n\n".join(d.page_content for d in docs)

    top_species = predictions[0]["species"] if predictions else "Unknown species"

    prompt = f"""You are an expert Maasai Mara wildlife guide helping a tourist.

The tourist photographed an animal. The top prediction is: {top_species}

All predictions:
{predictions}

Relevant wildlife knowledge:
{context}

Tourist's question: {question}

Answer using only the information in the knowledge above.
Be friendly, engaging, and concise (2-4 sentences).
If the context does not contain enough information, say so honestly.
"""

    try:
        response = _llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        raise
