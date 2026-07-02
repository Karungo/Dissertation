from services.vector_loader import (
    load_vectorstore
)
def retrieve_context(
    species,
    question
):

    vectorstore = (
        load_vectorstore()
    )

    docs = vectorstore.similarity_search(
        query=f"{species} {question}",
        k=5
    )

    return docs

