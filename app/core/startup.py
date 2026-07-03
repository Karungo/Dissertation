from contextlib import asynccontextmanager
import asyncio

from ml.loader import load_model
from rag.vectorstore import load_vectorstore


@asynccontextmanager
async def lifespan(app):

    loop = asyncio.get_running_loop()

    model_task = loop.run_in_executor(
        None,
        load_model
    )

    vector_task = loop.run_in_executor(
        None,
        load_vectorstore
    )

    await asyncio.gather(
        model_task,
        vector_task
    )

    yield
