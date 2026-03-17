import os
import tempfile
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import modular components
from core.config import OPENROUTER_API_KEY
from core.database import vectorstore
from agents.factory import get_r2cell_agent

# ==========================================
# Konfigurasi Awal
# ==========================================
os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memori Sederhana (Disimpan di RAM)
# Format: {"session_id": [{"role": "user", "content": "..."}, ...]}
chat_histories = {}

# ==========================================
# Endpoint API
# ==========================================

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as temp_file:
            temp_file.write(await file.read())
            temp_path = temp_file.name

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(temp_path)
        elif file.filename.endswith(".txt"):
            loader = TextLoader(temp_path)
        else:
            os.remove(temp_path)
            raise HTTPException(status_code=400, detail="Hanya mendukung file PDF atau TXT.")

        dokumen = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(dokumen)

        vectorstore.add_documents(chunks)
        os.remove(temp_path)

        return {"message": f"Dokumen '{file.filename}' berhasil diproses dan disimpan di Chroma DB!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat_endpoint(message: str = Form(...), session_id: str = Form("default_session")):
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    history = chat_histories[session_id]
    agent = get_r2cell_agent()

    # Gabungkan history + pesan baru dalam format messages
    messages = history + [{"role": "user", "content": message}]

    try:
        result = agent.invoke({"messages": messages})

        # Ambil response terakhir dari AI
        output = result["messages"][-1].content

        # Simpan ke memori dalam format messages
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": output})
        chat_histories[session_id] = history

        return {"response": output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))