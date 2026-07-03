import os
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)

def generate_answer(question, predictions, docs):

    context = "\n\n".join(d.page_content for d in docs)

    prompt = f"""
You are a wildlife expert.

Predictions:
{predictions}

Context:
{context}

Question:
{question}

Answer using only context.
"""

    return llm.invoke(prompt).content
