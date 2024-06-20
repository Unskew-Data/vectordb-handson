# Hands on with Vector databases

Basics of VectorDB

## Setup
1. Clone and cd into this repository and run
```shell
pip install poetry
poetry install
# activate the venv
```
or
```shell
# create an env using for ex. conda
pip install -r requirements.txt
```

2. Spin up a local qdrant image on docker
```shell
docker-compose up -d
```

3. Verify that your qdrant database is up and running
```shell
curl localhost:6333/readyz
```
You should get a response:
> all shards are ready

## About the dataset
The dataset is extracted from Confluence from the `NEWS` space.
Details around the dataset creation are under: `vectordb_blog/setup`.

The dataset is available under `data/confluence.json`: [here](./data/confluence.json)
There are some handy util functions in `vectordb_blog/utils.py`.

#### Pre-requisites
1. OpenAI credentials (for both embedding and GPT)
2. Dataset under `data/confluence.json`
3. (*Optional*) Confluence API Token (if you want to try creating the dataset as well)

## Part 1: Create the collection
1. Use the installed `qdrant_client` package to create the qdrant collection.
2. You can refer to the docs [here](https://qdrant.tech/documentation/concepts/collections/#create-a-collection)
3. Explore the various configurations that the client provides:
- `hnsw_config`
- `wal_config`
- `shard_number`
- `quantization_config`

4. If we had around 10,000 pages to index, how would we create the collection to optimize latency and resource usage?

## Part 2: Indexing into Qdrant
We need the Azure OpenAI API Keys for this to work. Adapt accordingly for other providers.

1. Each page has large content. We have to chunk the page by the token size of the embedding model we're using.
2. For each chunk, we'll get the embedding using our embedding provider (for ex. OpenAI, Azure OpenAI, Self-hosted multilingual-e5)
3. Include relevant metadata in the payload of each point (for ex. `page_id`, `space`, `url` for citations)
4. Don't forget to include the `content` with the page content in the payload as we'll be querying Qdrant using vectors and we'll be getting 
similar vectors as a response. We need the payload to get the content that the vector represents.
5. Finally, ingest your points into Qdrant. For better performance, always ingest in batches.

Documentation on indexing into Qdrant can be found [here](https://qdrant.tech/documentation/concepts/points/#upload-points)

## Part 3: Querying the collection
Refer [here](https://qdrant.tech/documentation/concepts/search/#search-api)

1. Create an AzureOpenAI client as we'll be using it to embed our query.
2. Query Qdrant using the `search` API:
- Only pages under the `DAPL` space. We should have this in our payload.
- Query using both exact KNN and ANN
3. Play around with the various query parameters and hnsw config for search.

## Part 4: Retrieval Augmented Generation (RAG) using Qdrant
Refer [here](https://python.langchain.com/v0.1/docs/use_cases/question_answering/quickstart/)
We'll be using langchain and its openai and qdrant modules.

1. Create the embeddings and llm clients for constructing the RAG.
2. Construct the langchain vectorstore client for Qdrant using the `langchain_qdrant` package.
3. The Vector store retriever should use search of type `similarity` and only take the top 5 most similar documents.
4. Construct a custom prompt using `langchain_core.prompts.PromptTemplate`.
5. Chain together the various pieces of the RAG
6. Invoke the RAG with a question that takes in the Confluence pages as context from Qdrant.

How would you extend this result with citations? Remember we have the `url` stored in the payload of the Qdrant points.


### Reference Links:
- [RAG citations](https://python.langchain.com/v0.2/docs/how_to/qa_citations/#cite-documents)
- [HNSW](https://www.pinecone.io/learn/series/faiss/hnsw/)
- [Qdrant Concepts](https://qdrant.tech/documentation/concepts/)
