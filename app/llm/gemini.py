import logging
from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GEMINI_API_KEY, GEMINI_MODEL

logger = logging.getLogger(__name__)

_llm = ChatGoogleGenerativeAI(
    model=GEMINI_MODEL,
    google_api_key=GEMINI_API_KEY,
    temperature=0.2
)

PROMPT_TEMPLATE = """You are an expert Maasai Mara wildlife guide helping a tourist.

VISION ANALYSIS RESULTS
-----------------------
Animals detected (YOLOv8 + EfficientNet-B4):
{species_summary}

Scene analysis (OpenCV):
  Habitat     : {habitat}
  Time of day : {time_of_day}
  Vegetation  : {vegetation_ratio:.1%} green cover
  Water nearby: {water_ratio:.1%}

KNOWLEDGE BASE CONTEXT
----------------------
{context}

SOURCES USED
------------
{sources}

TOURIST QUESTION
----------------
{question}

INSTRUCTIONS
------------
- Answer using ONLY the information provided above.
- Reference the habitat and time of day where relevant.
- If multiple animals are detected, address each one briefly.
- If context lacks enough information, say so honestly — do not hallucinate.
- Be friendly, engaging, and concise (3-5 sentences).

Answer:"""


def generate_answer(
    detections: list,
    habitat: dict,
    context: str,
    sources: list,
    question: str
) -> str:
    """Generate a grounded tourist-friendly answer using Gemini."""

    species_summary = "\n".join(
        f"  {i+1}. {d['species']} ({d['species_conf']:.1%}) "
        f"[YOLO: {d['yolo_label']} {d['yolo_conf']:.1%}] "
        f"Top-3: {[(t['species'], f\"{t['confidence']:.1%}\") for t in d['top3']]}"
        for i, d in enumerate(detections)
    )

    sources_str = "\n".join(sources) if sources else "No sources retrieved."

    if not context.strip():
        context = "No specific knowledge base entries found for the detected species."

    prompt = PROMPT_TEMPLATE.format(
        species_summary  = species_summary,
        habitat          = habitat["habitat"],
        time_of_day      = habitat["time_of_day"],
        vegetation_ratio = habitat["vegetation_ratio"],
        water_ratio      = habitat["water_ratio"],
        context          = context,
        sources          = sources_str,
        question         = question,
    )

    try:
        response = _llm.invoke(prompt)
        return response.content
    except Exception as e:
        logger.error(f"Gemini generation failed: {e}")
        raise
