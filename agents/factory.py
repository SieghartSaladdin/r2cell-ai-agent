from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END
from langgraph.graph import MessagesState
from langgraph.types import interrupt
from langchain_core.messages import AIMessage, RemoveMessage, ToolMessage
from core.config import OPENROUTER_API_KEY, MODEL_NAME, OPENROUTER_BASE_URL, MAX_HISTORY_MESSAGES
from langchain_core.tools import tool
from tools.document import pencarian_dokumen
from agents.prompts import SYSTEM_PROMPT
from core.database import pg_checkpointer



@tool
def tanya_admin_diskon(pertanyaan_ke_admin: str) -> str:
    """Gunakan tool ini HANYA jika pengguna meminta diskon secara spesifik.
    Kirimkan pertanyaan ke admin untuk menanyakan persetujuan diskon.
    Contoh: "Halo admin, ada user yang minta diskon iPhone 15 Pro, mau dikasih berapa?"
    """
    # Menghentikan (interrupt) eksekusi dan mengirim pertanyaan ke UI Admin
    balasan_admin = interrupt({
        "question": pertanyaan_ke_admin,
        "type": "discount_negotiation"
    })
    
    # Nilai ini adalah jawaban yang diketik oleh admin di UI
    return balasan_admin

def get_r2cell_agent():
    llm = ChatOpenAI(
        openai_api_base=OPENROUTER_BASE_URL,
        openai_api_key=OPENROUTER_API_KEY,
        model_name=MODEL_NAME,
        temperature=0,
        default_headers={
            "HTTP-Referer": "http://localhost:8000", # Wajib untuk OpenRouter di beberapa kondisi
            "X-Title": "R2Cell AI Agent"
        }
    )
    tools = [pencarian_dokumen, tanya_admin_diskon]
    
    # Fungsi modifier untuk membatasi jumlah percakapan memori
    def manage_memory_limit(state):
        messages = state["messages"]
        # Hitung jumlah pesan saat ini
        if len(messages) > MAX_HISTORY_MESSAGES:
            # Ambil pesan-pesan awal yang harus dihapus (kecuali SystemMessage jika ada di indeks 0)
            # Karena prompt kita masukkan lewat `state_modifier`/`prompt` dari create_react_agent,
            # messages murni hanya obrolan user & AI
            messages_to_remove = messages[:-MAX_HISTORY_MESSAGES]
            
            # Kita kembalikan RemoveMessage() untuk identifikasi ID pesan yang dibuang
            return [RemoveMessage(id=m.id) for m in messages_to_remove]
        return []
    
    # Kita gunakan Agent built-in React, namun jalurnya dimanipulasi dengan Graph manual.
    # Kita kembalikan penggunaan create_react_agent secara langsung
    # karena kita sudah membungkus interupsinya ke dalam sebuah custom Tool (tanya_admin_diskon)
    agent = create_react_agent(
        llm, 
        tools,
        prompt=SYSTEM_PROMPT,
        checkpointer=pg_checkpointer.get_saver()
    )
    
    return agent
