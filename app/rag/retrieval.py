from rag.vectorstore import load_vectorstore


def retrieve_context(species, question):

    vectorstore = load_vectorstore()

    return vectorstore.similarity_search(
        f"{species} {question}",
        k=3
    )
