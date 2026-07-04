import logging
from rag.vectorstore import load_vectorstore

logger = logging.getLogger(__name__)


def retrieve_context(species: str, question: str, k: int = 5) -> list:
    """
    Retrieve the top-k most relevant documents for a given species and question.
    """
    vs    = load_vectorstore()
    query = f"{species} {question}"
    docs  = vs.similarity_search(query, k=k)
    logger.info(f"Retrieved {len(docs)} docs for query: '{query[:60]}'")
    return docs
