from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import GEMINI_API_KEY

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY
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

Answer only using context.
"""

    return llm.invoke(prompt).content
