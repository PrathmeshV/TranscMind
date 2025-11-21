"""ONNX classifier wrapper with a graceful stub fallback when model or runtime not available."""
import os
import json
from typing import Tuple

try:
    import onnxruntime as ort
    import numpy as np
    _HAS_ORT = True
except Exception:
    ort = None
    import math as np
    _HAS_ORT = False

try:
    import shap
    _HAS_SHAP = True
except Exception:
    shap = None
    _HAS_SHAP = False


class StubClassifier:
    def __init__(self, taxonomy_path: str = 'api/models/taxonomy.json'):
        try:
            with open(taxonomy_path, 'r', encoding='utf-8') as f:
                tax = json.load(f)
                self.labels = tax.get('labels', ['others'])
        except Exception:
            self.labels = ['others']

    def predict(self, embedding) -> Tuple[str, float, list]:
        # Return first label as high-confidence stub
        probs = [0.0] * len(self.labels)
        probs[0] = 0.95
        return self.labels[0], 0.95, probs

    def shap_explain(self, embedding):
        # return a minimal fake SHAP payload
        try:
            length = len(embedding) if hasattr(embedding, '__len__') else 1
        except Exception:
            length = 1
        return {'shap_values': [[0.0] * length]}


class ONNXClassifier:
    def __init__(self, model_path: str = 'api/models/model.onnx'):
        self.model_path = model_path
        self.session = None
        self.input_name = None
        self.output_name = None
        self.taxonomy = {'labels': ['others']}

        # load taxonomy
        try:
            with open('api/models/taxonomy.json', 'r', encoding='utf-8') as f:
                self.taxonomy = json.load(f)
        except Exception:
            # leave default
            pass

        # attempt to create ONNX runtime session
        if _HAS_ORT and os.path.exists(model_path):
            try:
                quant_path = model_path.replace('.onnx', '.quant.onnx')
                use_path = quant_path if os.path.exists(quant_path) else model_path
                self.session = ort.InferenceSession(use_path, providers=['CPUExecutionProvider'])
                self.input_name = self.session.get_inputs()[0].name
                self.output_name = self.session.get_outputs()[0].name
            except Exception:
                self.session = None

        # if session not created, replace with stub
        if self.session is None:
            self._stub = StubClassifier()
        else:
            self._stub = None

    def predict(self, embedding):
        if self._stub is not None:
            return self._stub.predict(embedding)

        # ONNX expects batch dim and float32 numpy
        inp = np.array(embedding, dtype=np.float32)
        if inp.ndim == 1:
            inp = inp.reshape(1, -1)
        preds = self.session.run([self.output_name], {self.input_name: inp})[0]
        probs = self._softmax(preds)[0]
        idx = int(np.argmax(probs))
        return self.taxonomy.get('labels', ['others'])[idx], float(probs[idx]), probs.tolist()

    def _softmax(self, x):
        e_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return e_x / e_x.sum(axis=1, keepdims=True)

    def shap_explain(self, embedding):
        # Use KernelExplainer if available, otherwise return stub
        if self._stub is not None:
            return self._stub.shap_explain(embedding)

        if not _HAS_SHAP:
            return {'shap_values': ['shap not available']}

        try:
            background = np.zeros((1, len(embedding)), dtype=np.float32)

            def f(x):
                if x.ndim == 1:
                    x = x.reshape(1, -1)
                preds = self.session.run([self.output_name], {self.input_name: x.astype(np.float32)})[0]
                return self._softmax(preds)

            explainer = shap.KernelExplainer(f, background)
            shap_vals = explainer.shap_values(np.array(embedding).reshape(1, -1), nsamples=30)
            vals = [v.tolist() for v in shap_vals]
            return {'shap_values': vals}
        except Exception as e:
            return {'error': str(e)}
