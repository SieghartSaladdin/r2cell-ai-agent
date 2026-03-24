from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from psycopg_pool import ConnectionPool
from langgraph.checkpoint.postgres import PostgresSaver
from core.config import CHROMA_PERSIST_DIR, EMBEDDING_MODEL, POSTGRES_DB_URI

embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
vectorstore = Chroma(persist_directory=CHROMA_PERSIST_DIR, embedding_function=embeddings)

class PostgresCheckpointer:
    def __init__(self):
        self.pool = None
        self.saver = None

    def connect(self):
        self.pool = ConnectionPool(
            conninfo=POSTGRES_DB_URI,
            max_size=20,
            kwargs={"autocommit": True, "prepare_threshold": 0}
        )
        self.saver = PostgresSaver(self.pool)
        self.saver.setup()

    def disconnect(self):
        if self.pool:
            self.pool.close()
            self.pool = None

    def get_saver(self):
        if not self.saver:
            self.connect()
        return self.saver

pg_checkpointer = PostgresCheckpointer()

def delete_document_by_source(source_path: str):
    try:
        # Menghapus dokumen dari koleksi Chroma berdasarkan metadata 'source'
        vectorstore._collection.delete(where={"source": source_path})
        return True
    except Exception as e:
        print(f"Error deleting from Chroma: {e}")
        return False
