"""Embedder wrapper with a lightweight stub fallback when SentenceTransformer or model isn't available."""
import os
try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    _HAS_ST = True
except Exception:
    SentenceTransformer = None
    import math as np
    _HAS_ST = False


class StubEmbedder:
    def __init__(self, dim: int = 384):
        self.dim = dim

    def embed(self, texts):
        # deterministic small embedding per input
        out = []
        for i, _ in enumerate(texts):
            vec = [0.001 * ((i + 1) % 10 + j % 10) for j in range(self.dim)]
            out.append(vec)
        return out


class Embedder:
    def __init__(self, model_name: str = 'sentence-transformers/all-MiniLM-L6-v2'):
        self.model_name = model_name
        self.is_stub = False
        if _HAS_ST:
            try:
                self.model = SentenceTransformer(model_name)
            except Exception:
                # fallback to stub if model cannot be loaded (network/offline)
                self.model = StubEmbedder()
                self.is_stub = True
        else:
            self.model = StubEmbedder()
            self.is_stub = True

    def embed(self, texts):
        if getattr(self.model, 'encode', None):
            try:
                embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
                return embs
            except Exception:
                # fallback to stub behavior
                return StubEmbedder().embed(texts)
        else:
            return self.model.embed(texts)
