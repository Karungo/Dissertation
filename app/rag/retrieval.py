from rag.vectorstore import get_vectorstore

def retrieve_context(species, question):
    vectorstore = get_vectorstore()

    return vectorstore.similarity_search(
        query=f"{species} {question}",
        k=5
    )
