# AI Document Agent & Chat

Proyek ini adalah aplikasi web sederhana yang memungkinkan pengguna untuk mengunggah dokumen (PDF/TXT) dan melakukan tanya jawab (Chat) dengan AI berdasarkan isi dokumen tersebut menggunakan RAG (Retrieval-Augmented Generation).

## 🚀 Fitur

- **Upload Dokumen**: Mendukung format PDF dan TXT.
- **RAG (Retrieval-Augmented Generation)**: Dokumen diproses, dipecah menjadi chunks, dan disimpan ke database vektor (ChromaDB).
- **Interactive Chat**: Tanya jawab dengan AI menggunakan context dari dokumen yang diunggah.
- **Modern Interface**: Antarmuka web sederhana menggunakan HTML/FastAPI.
- **Modular Architecture**: Kode terbagi menjadi core, agents, dan tools.

## 🛠️ Teknologi yang Digunakan

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **AI Framework**: [LangChain](https://www.langchain.com/)
- **Vector Database**: [ChromaDB](https://www.trychroma.com/)
- **LLM Provider**: OpenRouter (Model: hunter-alpha)
- **Embeddings**: Local Embedding (Gemma via Ollama)

## 📋 Struktur Folder

```
.
├── agents/             # Konfigurasi AI Agent dan Prompts
├── core/               # Konfigurasi aplikasi dan database
├── tools/              # Alat bantu (tools) untuk agent
├── chroma_data/        # Database vektor (ChromaDB)
├── main.py             # Entry point FastAPI
├── index.html          # Frontend sederhana
├── requirements.txt    # Daftar dependensi Python
└── .gitignore          # File exclude untuk Git
```

## ⚙️ Persiapan & Instalasi

1. **Clone Repository**
   ```bash
   git clone https://github.com/username/project-name.git
   cd project-name
   ```

2. **Buat Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   .\venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Dependensi**
   ```bash
   pip install -r requirements.txt
   ```

4. **Konfigurasi Environment**
   Buat file `.env` atau atur API Key di `core/config.py`.
   Pastikan Ollama berjalan untuk embedding jika menggunakan model lokal.

## 🏃 Menjalankan Aplikasi

Jalankan server menggunakan uvicorn:

```bash
uvicorn main:app --reload
```

Akses aplikasi di browser melalui: `http://127.0.0.1:8000`

## 📄 Lisensi
[MIT License](LICENSE)
