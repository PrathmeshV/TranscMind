# TransacMind

**TransacMind** is a fully local, end-to-end **AI-based financial transaction categorisation system** designed for experimentation and single-machine deployment.  
It classifies raw transaction text into meaningful categories and provides **confidence scores, explainability, and reasoning**, without relying on any external or paid APIs.

The project is built entirely using **free and open-source tools** and follows a production-style architecture with monitoring, feedback, and benchmarking support.

---

## 🌊 Data Flow Diagram

The core logic runs inside a **FastAPI inference service**.  
The diagram below illustrates how data flows through the system during a prediction request.

![TransacMind Data Flow](./dataflow.png)

---

## How the Project Works

The system processes each transaction through the following stages:

1. **Preprocessing**  
   Raw transaction text is cleaned and normalized (case handling, noise removal).

2. **Embedding**  
   Sentence embeddings are generated using **Sentence-BERT** when available.  
   If heavy libraries are not installed, a deterministic fallback embedding is used so the system can still run.

3. **Classification**  
   An **ONNX-based classifier** predicts the transaction category along with a confidence score.  
   If the ONNX model is unavailable, a safe stub classifier is used.

4. **RAG (Retrieval-Augmented Generation)**  
   The system retrieves similar example transactions and category rationales:
   - Uses **ChromaDB** when installed
   - Falls back to a local `.npz` store with `NearestNeighbors` when unavailable

5. **Agentic AI Layer**  
   A lightweight agent attempts to use **LangChain with a local LLM** to generate a reasoning summary.  
   If not available, a deterministic explanation is generated instead.

6. **Explainability**  
   SHAP-style explanations are returned when SHAP is installed; otherwise, a guarded fallback is used.

This fallback-first design ensures the application **always runs**, even with minimal dependencies.

---

## Key Features

- Fully local inference (no third-party API calls)
- Configurable category taxonomy (`taxonomy.json`)
- Explainable predictions using RAG and SHAP
- Agentic reasoning layer with safe fallbacks
- Human-in-the-loop feedback support
- Transparent latency and throughput benchmarking
- 100% free and open-source stack

---

## How to Run the Project (Windows – PowerShell)

### Step-by-step: Local run (PowerShell) 1. Open PowerShell and change to the project directory:
powershell
Set-Location -Path "F:\\TransacMind\\transactmind"

2. Create a virtual environment (one-time):
powershell
python -m venv .venv

3. Activate the venv:
powershell
. .venv\\Scripts\\Activate.ps1

4. Install core dependencies (small set to start the service):
powershell
pip install -r requirements-core.txt

5. (Optional) Install full dependencies for RAG/LLM/Streamlit/SHAP:
powershell
pip install -r requirements-full.txt

6. (Optional) Train and export a tiny ONNX model (demo dataset) — this writes api/models/model.onnx and a quantized version when possible:
powershell
python .\\training\\export_to_onnx.py

7. Build the local RAG store (if you want the local NPZ fallback filled from api/models/taxonomy.json):
powershell
python .\\api\\rag\\build_rag_db.py
This will attempt to use ChromaDB. If unavailable it creates api/rag/local_store.npz using the embedder (or a deterministic fallback).

8. Start the FastAPI server (development):
powershell
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000
Note: The server listens on 0.0.0.0 (all interfaces). Use http://127.0.0.1:8000/ or http://localhost:8000/docs in a browser. If accessing from another machine, use the host's LAN IP and ensure the firewall allows inbound traffic on 8000. 

9. Run the local smoke test (calls the running app):
powershell
python .\\scripts\\run_predict_local.py

10. Example manual POST (PowerShell):
powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/predict" -Method POST -ContentType "application/json" -Body '{"transaction_text":"buy milk from supermarket"}'
11. If you want to run the pytest smoke-test that imports the real app, run:
powershell
pytest -q tests/smoke_test_real.py

12. Run the Streamlit feedback / XAI UI (optional):
powershell
streamlit run dashboard/feedback_ui.py

13. Start services with Docker Compose (optional, when using dockerized Chromadb/Prometheus/Grafana):
powershell
cd docker
docker-compose up --build

14. Run Locust load tests (optional):
powershell
locust -f locustfile.py --host=http://127.0.0.1:8000

