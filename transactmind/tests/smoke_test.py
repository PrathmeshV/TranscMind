from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.testclient import TestClient
import os
import json

# Simple smoke-test FastAPI app mirroring the /predict flow but using light-weight stubs
app = FastAPI()

class PredictRequest(BaseModel):
    transaction_text: str

# simple preprocess
def preprocess_text(text: str) -> str:
    return " ".join(text.split())

# tiny embedder stub: returns fixed-size small vector (miniLM uses 384 dims)
class StubEmbedder:
    def __init__(self, dim: int = 384):
        self.dim = dim
    def embed(self, texts):
        return [[0.01 * (i+1) for i in range(self.dim)] for _ in texts]

# tiny classifier stub: uses taxonomy file if available
class StubClassifier:
    def __init__(self, taxonomy_path='api/models/taxonomy.json'):
        self.labels = ['others']
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                tax = json.load(f)
                self.labels = tax.get('labels', self.labels)
        except Exception:
            pass
    def predict(self, emb):
        # deterministic stub: pick first label with high confidence
        probs = [0.0] * len(self.labels)
        probs[0] = 0.95
        return self.labels[0], 0.95, probs
    def shap_explain(self, emb):
        # tiny fake SHAP explanation
        return {'shap_values': [[0.0] * len(emb)]}

# tiny RAG stub
class StubRAG:
    def explain(self, text, category):
        return f"Found example transactions supporting category '{category}'."

# tiny Agent stub
class StubAgent:
    def summarize(self, text, category, confidence, rag_exp):
        return f"Summary: predicted {category} ({confidence:.2f}). {rag_exp}"

@app.post('/predict')
def predict(req: PredictRequest):
    text = preprocess_text(req.transaction_text)
    emb = app.state.embedder.embed([text])[0]
    category, confidence, _ = app.state.classifier.predict(emb)
    rag_exp = app.state.rag.explain(text, category)
    agent_summary = app.state.agent.summarize(text, category, confidence, rag_exp)
    return {
        'category': category,
        'confidence': float(confidence),
        'rag_explanation': rag_exp,
        'agent_summary': agent_summary,
        'shap': app.state.classifier.shap_explain(emb)
    }

if __name__ == '__main__':
    # attach stubs
    app.state.embedder = StubEmbedder()
    app.state.classifier = StubClassifier(taxonomy_path=os.path.join(os.getcwd(), 'api', 'models', 'taxonomy.json'))
    app.state.rag = StubRAG()
    app.state.agent = StubAgent()

    client = TestClient(app)
    payload = {'transaction_text': 'Walmart Supercenter 1234 - Grocery purchase'}
    resp = client.post('/predict', json=payload)
    print('Status code:', resp.status_code)
    try:
        print('Response JSON:')
        print(json.dumps(resp.json(), indent=2))
    except Exception:
        print('Response text:', resp.text)
