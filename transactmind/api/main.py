from fastapi import FastAPI
from pydantic import BaseModel
from api.inference.preprocess import preprocess_text
from api.inference.embedder import Embedder
from api.inference.classifier import ONNXClassifier
from api.rag.rag_engine import RAGEngine
from api.agents.agent_controller import AgentController
from api.utils.config import settings
from prometheus_client import Counter, Histogram, make_asgi_app
import time

app = FastAPI(title="TransactMind API")

REQUEST_COUNT = Counter('transactmind_requests_total', 'Total number of requests')
REQUEST_LATENCY = Histogram('transactmind_request_latency_seconds', 'Request latency seconds')

class PredictRequest(BaseModel):
    transaction_text: str

@app.on_event("startup")
async def startup_event():
    # initialize components with defensive fallbacks when models or packages are unavailable
    try:
        app.state.embedder = Embedder()
    except Exception:
        from api.inference.embedder import StubEmbedder
        app.state.embedder = StubEmbedder()

    try:
        app.state.classifier = ONNXClassifier(settings.MODEL_PATH)
        # if classifier ended up as a stub property use it directly
    except Exception:
        # fallback to stub classifier
        from api.inference.classifier import StubClassifier
        app.state.classifier = StubClassifier()

    try:
        # try to create real RAG engine, else fallback to stub
        rag = RAGEngine()
        # ensure collection attribute exists, else use stub
        if getattr(rag, 'collection', None) is None:
            from api.rag.rag_engine import StubRAG
            app.state.rag = StubRAG()
        else:
            app.state.rag = rag
    except Exception:
        from api.rag.rag_engine import StubRAG
        app.state.rag = StubRAG()

    try:
        app.state.agent = AgentController()
    except Exception:
        # AgentController already falls back to None agent; provide minimal stub
        class MinimalAgent:
            def summarize(self, text, category, confidence, rag_exp):
                return f"Predicted '{category}' with confidence {confidence:.2f}. Rationale: {rag_exp}"
        app.state.agent = MinimalAgent()

@app.post('/predict')
async def predict(req: PredictRequest):
    REQUEST_COUNT.inc()
    start = time.time()
    text = preprocess_text(req.transaction_text)
    emb = app.state.embedder.embed([text])[0]
    category, confidence, raw_scores = app.state.classifier.predict(emb)
    rag_exp = app.state.rag.explain(text, category)
    agent_summary = app.state.agent.summarize(text, category, confidence, rag_exp)
    elapsed = time.time() - start
    REQUEST_LATENCY.observe(elapsed)
    return {
        'category': category,
        'confidence': float(confidence),
        'rag_explanation': rag_exp,
        'agent_summary': agent_summary,
        'shap': app.state.classifier.shap_explain(emb)
    }

# mount prometheus ASGI app
app.mount('/metrics', make_asgi_app())
