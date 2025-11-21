import numpy as np
from sklearn.metrics import classification_report
import joblib

def evaluate(pkl_model='api/models/model.onnx.pkl', X=None, y=None):
    clf = joblib.load(pkl_model)
    preds = clf.predict(X)
    print(classification_report(y, preds))
