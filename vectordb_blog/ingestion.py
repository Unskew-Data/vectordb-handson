"""
    Ingestion: 
        Content -> Chunk -> Embedding -> Ingest into Qdrant with payload
"""

from __future__ import annotations
import uuid
import json
import openai
from qdrant_client import QdrantClient, models
from qdrant_client.http.exceptions import UnexpectedResponse
from tqdm import tqdm
from vectordb_blog.utils import batched, get_embedding
from vectordb_blog.config import config


def ingest_into_qdrant(client: QdrantClient, oa_client: openai.AzureOpenAI):

    with open(config.DATA_PATH, "r") as f:
        lines = f.readlines()

        for line in tqdm(lines):
            if line:
                points = []
                page = json.loads(line)
                content = page["content"]
                chunks = batched(content, config.TOKEN_SIZE)

                for chunk in chunks:
                    # TODO: can batch this for better performance
                    vector = get_embedding(oa_client, "".join(chunk))

                    points.append(
                        models.PointStruct(
                            id=str(uuid.uuid4()),
                            vector=vector,
                            payload={
                                "page_id": page["id"],
                                "space": page["space"],
                                "url": page["url"],
                                "content": "".join(chunk),
                            },
                        )
                    )

                for batch in batched(points, 20):
                    client.upsert(
                        collection_name=config.QDRANT_COLLECTION_NAME,
                        points=list(batch),
                    )

    print("Done.")


if __name__ == "__main__":
    openai_client = openai.AzureOpenAI(
        api_key=config.OPENAI_API_KEY,
        api_version=config.OPENAI_API_VERSION,
        azure_endpoint=config.OPENAI_ENDPOINT,
    )

    qdrant_client = QdrantClient(url="localhost", port=6333, api_key=None)

    # collection creation
    try:
        qdrant_client.create_collection(
            collection_name=config.QDRANT_COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=config.VECTOR_SIZE, distance=models.Distance.COSINE
            ),
        )

        # add payload indexes
        qdrant_client.create_payload_index(
            collection_name=config.QDRANT_COLLECTION_NAME,
            field_name="space",
            field_schema="keyword",
        )

    except UnexpectedResponse as e:
        print("Collection exists!")

    ingest_into_qdrant(qdrant_client, openai_client)
