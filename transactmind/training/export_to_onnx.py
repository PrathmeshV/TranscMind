import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
import joblib
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
import json
import os
from onnxruntime.quantization import quantize_dynamic, QuantType


def generate_dummy_data(taxonomy_path='api/models/taxonomy.json', n_per_label=50):
    with open(taxonomy_path, 'r', encoding='utf-8') as f:
        tax = json.load(f)
    labels = tax['labels']
    texts = []
    ys = []
    for i, lab in enumerate(labels):
        for j in range(n_per_label):
            texts.append(f"{lab} example transaction {j}")
            ys.append(i)
    return texts, np.array(ys)


def train_and_export(model_out='api/models/model.onnx', taxonomy_path='api/models/taxonomy.json'):
    texts, ys = generate_dummy_data(taxonomy_path)
    embedder = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    X = embedder.encode(texts, convert_to_numpy=True, show_progress_bar=True)
    clf = LogisticRegression(max_iter=200)
    clf.fit(X, ys)
    initial_type = [('float_input', FloatTensorType([None, X.shape[1]]))]
    onx = convert_sklearn(clf, initial_types=initial_type)
    with open(model_out, 'wb') as f:
        f.write(onx.SerializeToString())
    joblib.dump(clf, model_out + '.pkl')
    print('Exported ONNX to', model_out)
    quant_out = model_out.replace('.onnx', '.quant.onnx')
    try:
        quantize_dynamic(model_out, quant_out, weight_type=QuantType.QInt8)
        print('Quantized ONNX written to', quant_out)
    except Exception as e:
        print('Quantization failed:', e)

if __name__ == '__main__':
    os.makedirs(os.path.dirname(os.path.abspath('api/models/model.onnx')), exist_ok=True)
    train_and_export()
