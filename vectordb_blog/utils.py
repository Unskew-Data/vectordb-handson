from __future__ import annotations
import openai
from vectordb_blog.config import config


def batched(iterable, n: int):
    from itertools import islice

    if n < 1:
        raise ValueError("n > = 1")

    it = iter(iterable)

    while batch := tuple(islice(it, n)):
        yield batch


def get_embedding(client: openai.AzureOpenAI, text: str) -> list[float]:
    response = client.embeddings.create(model=config.MODEL_NAME, input=text)

    return response.data[0].embedding
