import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
MODEL_NAME = "openrouter/hunter-alpha"
EMBEDDING_MODEL = "embeddinggemma:latest"
CHROMA_PERSIST_DIR = "./chroma_data"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
