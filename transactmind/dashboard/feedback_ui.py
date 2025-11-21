import streamlit as st
import pandas as pd
from datetime import datetime
import os

DATA_PATH = os.path.join(os.getcwd(), 'data', 'feedback.csv')

st.title('TransactMind Feedback')

st.write('Provide corrections for low-confidence predictions')

with st.form('feedback'):
    text = st.text_area('Transaction text')
    predicted = st.text_input('Predicted category')
    correct = st.text_input('Correct category')
    notes = st.text_area('Notes (optional)')
    submitted = st.form_submit_button('Submit')
    if submitted:
        df = pd.DataFrame([{
            'timestamp': datetime.utcnow().isoformat(),
            'text': text,
            'predicted': predicted,
            'correct': correct,
            'notes': notes
        }])
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        if not os.path.exists(DATA_PATH):
            df.to_csv(DATA_PATH, index=False)
        else:
            df.to_csv(DATA_PATH, mode='a', header=False, index=False)
        st.success('Feedback saved')
