# TransactMind

Local, autonomous transaction categorisation system.

Components:

- FastAPI inference service (`api/`)
- ONNX classifier (export via `training/export_to_onnx.py`)
- Sentence-BERT embedder
- RAG engine backed by ChromaDB (or FAISS)
- Local agent (llama-cpp-python / TinyLlama)
- Streamlit feedback + SHAP dashboard
- Monitoring (Prometheus + Grafana)
- Docker + docker-compose for local orchestration

Quick start (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
.\scripts\setup_venv.ps1
# activate
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python .\training\export_to_onnx.py
python .\api\rag\build_rag_db.py
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

See `BENCHMARKS.md` for performance notes.
