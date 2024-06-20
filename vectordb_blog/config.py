import os
from dotenv import load_dotenv


class Config:
    load_dotenv()

    QDRANT_COLLECTION_NAME = "confluence"
    MODEL_NAME = "text-embedding-ada-002-2"
    TOKEN_SIZE = 8191
    VECTOR_SIZE = 1536
    DATA_PATH = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            os.path.pardir,
            os.path.pardir,
            "data",
            "confluence.json",
        )
    )

    # env vars
    CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
    CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
    CONFLUENCE_PAT = os.getenv("CONFLUENCE_PAT")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
    OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
    OPENAI_GPT_API_KEY = os.getenv("OPENAI_GPT_API_KEY")
    OPENAI_GPT_MODEL = os.getenv("OPENAI_GPT_MODEL")
    OPENAI_GPT_ENDPOINT = os.getenv("OPENAI_GPT_ENDPOINT")


config = Config()
