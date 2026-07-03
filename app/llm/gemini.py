from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)


def generate_answer(question, predictions, docs):

    context = "\n\n".join(
        d.page_content for d in docs
    )

    prompt = f"""
Predictions:
{predictions}

Context:
{context}

Question:
{question}

Answer using only the context.
"""

    return llm.invoke(prompt).content
