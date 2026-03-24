import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
MODEL_NAME = "nvidia/nemotron-3-super-120b-a12b:free"
EMBEDDING_MODEL = "embeddinggemma:latest"
CHROMA_PERSIST_DIR = "./chroma_data"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
POSTGRES_DB_URI = os.environ.get("POSTGRES_DB_URI")
MAX_HISTORY_MESSAGES = int(os.environ.get("MAX_HISTORY_MESSAGES", "5"))
