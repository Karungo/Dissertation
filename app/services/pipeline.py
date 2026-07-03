from PIL import Image
from ml.cnn import predict_species
from rag.retrieval import retrieve_context
from llm.gemini import generate_answer


async def analyze_image(upload_file, question):

    image = Image.open(upload_file.file)

    predictions = predict_species(image, top_k=3)

    docs = []
    for p in predictions:
        docs.extend(retrieve_context(p["species"], question))

    answer = generate_answer(question, predictions, docs)

    return {
        "predictions": predictions,
        "answer": answer
    }
