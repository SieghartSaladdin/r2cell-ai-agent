from langchain.tools import tool
from core.database import vectorstore

@tool(response_format="content_and_artifact")
def pencarian_dokumen(query: str):
    """Gunakan tool ini untuk mencari informasi dari dokumen yang telah diunggah oleh pengguna."""
    retrieved_docs = vectorstore.similarity_search(query, k=3)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs
