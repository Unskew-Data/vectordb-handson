"""
    Simple query patterns in Qdrant
"""

from pprint import pprint
from qdrant_client import QdrantClient, models
import openai
from vectordb_blog.config import config
from vectordb_blog.utils import get_embedding


client = QdrantClient(url="localhost", port=6333)
openai_client = openai.AzureOpenAI(
    api_key=config.OPENAI_API_KEY,
    api_version=config.OPENAI_API_VERSION,
    azure_endpoint=config.OPENAI_ENDPOINT,
)

query = """
    Whats the latest on the central bank interest rates?
"""

vector = get_embedding(openai_client, query)


results = client.search(
    collection_name=config.QDRANT_COLLECTION_NAME,
    query_filter=models.Filter(
        must=[models.FieldCondition(key="space", match=models.MatchValue(value="DAPL"))]
    ),
    search_params=models.SearchParams(hnsw_ef=128, exact=False),
    query_vector=vector,
    limit=5,
)

pprint([{"content": x.payload["content"], "url": x.payload["url"]} for x in results])
