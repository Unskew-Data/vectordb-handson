import os
from typing import Any
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient

from vectordb_blog.config import config


class QdrantWithPayload(Qdrant):
    """
    Official Langchain client does not return payload
    so overriding the document creation ;)
    """

    @classmethod
    def _document_from_scored_point(
        cls,
        scored_point: Any,
        collection_name: str,
        content_payload_key: str,
        metadata_payload_key: str,
    ) -> Document:
        # metadata = scored_point.payload.get(metadata_payload_key) or {}
        metadata = scored_point.payload

        metadata["_id"] = scored_point.id
        metadata["_collection_name"] = collection_name
        content = scored_point.payload.get(content_payload_key, "")

        metadata.pop(content_payload_key)

        return Document(
            page_content=content,
            metadata=metadata,
        )


# for embedding the query
embeddings = AzureOpenAIEmbeddings(
    model="text-embedding-ada-002-2",
    azure_endpoint=config.OPENAI_ENDPOINT,
    api_key=config.OPENAI_API_KEY,
    api_version=config.OPENAI_API_VERSION,
)

# for summarizing
llm = AzureChatOpenAI(
    azure_endpoint=config.OPENAI_GPT_ENDPOINT,
    azure_deployment=config.OPENAI_GPT_MODEL,
    api_key=config.OPENAI_GPT_API_KEY,
    api_version=config.OPENAI_API_VERSION,
)

# to retrieve the documents from qdrant
qdrant_client = QdrantClient(url="localhost:6333")
vectorstore = QdrantWithPayload(
    qdrant_client,
    collection_name=config.QDRANT_COLLECTION_NAME,
    embeddings=embeddings,
    content_payload_key="content",
)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})


# prompt to instruct chatgpt
template = """
Use the following pieces of context to answer the question at the end.
If you don't know the answer, just say that you don't know, don't try to make up an answer.
Always say "thanks for asking!" at the end of the answer.

{context}

Question: {question}

Helpful Answer:
"""

rag_prompt = PromptTemplate.from_template(template)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag = (
    {
        "context": retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | rag_prompt
    | llm
    | StrOutputParser()
)


answer = rag.invoke("Give me a summary of the top 10 news in technology.")


print(answer)

# TODO: extend with citations
