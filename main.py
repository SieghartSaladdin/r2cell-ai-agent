import os
import tempfile
from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Import modular components
from core.config import OPENROUTER_API_KEY
from core.database import vectorstore, delete_document_by_source, pg_checkpointer
from agents.factory import get_r2cell_agent

# ==========================================
# Konfigurasi Awal
# ==========================================
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "documents")
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

os.environ["OPENROUTER_API_KEY"] = OPENROUTER_API_KEY

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize PostgreSQL pool and tables
    try:
        pg_checkpointer.connect()
        print("Connected to PostgreSQL and setup checkpointer tables.")
    except Exception as e:
        print(f"Warning: Failed to connect to PostgreSQL. Please ensure the database exists and URI is correct. Error: {e}")
    yield
    # Shutdown: Close PostgreSQL pool
    pg_checkpointer.disconnect()
    print("Disconnected from PostgreSQL.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# Endpoint API
# ==========================================

@app.get("/")
def read_root():
    return FileResponse("index.html")

@app.get("/documents")
def list_documents():
    try:
        files = os.listdir(DOCUMENTS_DIR)
        return {"documents": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{filename}")
def get_document(filename: str):
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Dokumen tidak ditemukan")

@app.delete("/documents/{filename}")
def delete_document(filename: str):
    file_path = os.path.join(DOCUMENTS_DIR, filename)
    
    # 1. Hapus file fisik jika ada
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # 2. Hapus data dari vectorstore Chroma
    # LangChain document loaders biasanya menyimpan absolut path di metadata `source`
    # Kita panggil helper dari database.py
    success = delete_document_by_source(file_path)
    if not success:
        # Coba juga menghapus berdasarkan path relatif jika loader menggunakannya
        delete_document_by_source(filename)

    return {"message": f"Dokumen '{filename}' berhasil dihapus."}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        file_path = os.path.join(DOCUMENTS_DIR, file.filename)
        
        # Simpan file secara permanen
        with open(file_path, "wb") as f:
            f.write(await file.read())

        if file.filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
        elif file.filename.endswith(".txt"):
            loader = TextLoader(file_path)
        else:
            os.remove(file_path)
            raise HTTPException(status_code=400, detail="Hanya mendukung file PDF atau TXT.")

        dokumen = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""] # Ini agar dia berusaha tidak memotong baris
    )
        chunks = text_splitter.split_documents(dokumen)

        vectorstore.add_documents(chunks)

        return {"message": f"Dokumen '{file.filename}' berhasil diproses dan disimpan!"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_database():
    try:
        # Menghapus semua koleksi di ChromaDB
        vectorstore.delete_collection()
        return {"message": "Database berhasil di-reset (semua dokumen dihapus)."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal melakukan reset: {str(e)}")

from pydantic import BaseModel
from typing import Optional, Any
from langgraph.types import interrupt, Command

# Model untuk Resume Interrupt
class ResumeRequest(BaseModel):
    session_id: str
    admin_reply: str

@app.post("/chat")
async def chat_endpoint(message: str = Form(...), session_id: str = Form("default_session")):
    agent = get_r2cell_agent()
    config = {"configurable": {"thread_id": session_id}}

    try:
        # Jalankan agent
        result = agent.invoke(
            {"messages": [{"role": "user", "content": message}]},
            config=config
        )

        # Cek apakah ada interrupt (Human-in-the-loop)
        # Di LangGraph, jika ada interrupt, result akan mengandung informasi tersebut
        # Namun di API stateless, kita perlu mengecek state terakhir
        state = agent.get_state(config)
        
        if state.next: # Jika ada node selanjutnya yang tertunda (karena interrupt)
            # Ambil nilai interrupt terakhir
            interrupt_value = state.tasks[0].interrupts[0].value if state.tasks and state.tasks[0].interrupts else None
            
            # Ambil pesan AI terakhir yang menyebabkan Tool dieksekusi
            last_msg = result["messages"][-1]
            pending_message = ""
            
            if last_msg.type == "ai":
                if last_msg.content:
                    pending_message = last_msg.content
                else:
                    pending_message = "tunggu sebentar ya Kak, saya konfirmasi terlebih dahulu ke adminnya... ⏳"
                    
            return {
                "response": "Permintaan anda memerlukan persetujuan admin.",
                "pending_message": pending_message,
                "interrupt": True,
                "interrupt_value": interrupt_value
            }

        output = result["messages"][-1].content
        return {"response": output, "interrupt": False}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/resume")
async def resume_chat(request: ResumeRequest):
    agent = get_r2cell_agent()
    config = {"configurable": {"thread_id": request.session_id}}
    
    try:
        # Resume flow dengan Command
        result = agent.invoke(
            Command(resume=request.admin_reply),
            config=config
        )
        
        output = result["messages"][-1].content
        return {"response": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))