from rag.vectorstore import load_vectorstore

def retrieve_context(species, question):
    vs = load_vectorstore()

    return vs.similarity_search(
        query=f"{species} {question}",
        k=5
    )
