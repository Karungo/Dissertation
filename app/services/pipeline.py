from PIL import Image

from services.cnn_service import (
    predict_species
)

from services.retrieval_service import (
    retrieve_context
)

from services.gemini_service import (
    generate_answer
)

async def analyze_image(
    upload_file,
    question
):

    image = Image.open(
        upload_file.file
    )

    predictions = (
        predict_species(
            image,
            top_k=3
        )
    )

    docs = []

    for prediction in predictions:

        species = prediction[
            "species"
        ]

        docs.extend(
            retrieve_context(
                species,
                question
            )
        )

    answer = generate_answer(
        question,
        predictions,
        docs
    )

    return {
        "predictions":
            predictions,

        "answer":
            answer
    }
