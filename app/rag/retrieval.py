import logging
from rag.vectorstore import load_vectorstore

logger = logging.getLogger(__name__)


def retrieve_context(species: str, question: str, k: int = 6) -> list:
    """Retrieve and deduplicate top-k chunks for species + question."""
    vs    = load_vectorstore()
    docs  = vs.similarity_search(f"{species} {question}", k=k)
    seen, unique = set(), []
    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique.append(doc)
    logger.info(f"Retrieved {len(unique)} unique chunks for [{species}]")
    return unique
