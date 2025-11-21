import streamlit as st
import pandas as pd
import json
import os

st.title('TransactMind XAI Dashboard')

st.header('Category Distribution')
try:
    df = pd.read_csv(os.path.join(os.getcwd(), 'data', 'synthetic_transactions.csv'))
    st.bar_chart(df['category'].value_counts())
except Exception:
    st.info('No transaction dataset found at data/synthetic_transactions.csv')

st.header('SHAP Explanation')
shap_json = st.file_uploader('Upload SHAP json', type=['json'])
if shap_json:
    data = json.load(shap_json)
    st.json(data)
