import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Churn Demo", layout="wide")
st.title("📉 Telecom Churn Prediction — Demo")

uploaded = st.file_uploader("Upload CSV of active customers", type=["csv"])
top_n = st.slider("Show top-N at-risk customers", 5, 200, 50)

if st.button("Score") and uploaded:
    df = pd.read_csv(uploaded)
    payload = {"records": df.to_dict(orient="records")}
    res = requests.post("http://localhost:8000/predict", json=payload)
    probs = res.json()["probabilities"]
    df["churn_probability"] = probs
    df = df.sort_values("churn_probability", ascending=False)
    st.subheader("Ranked Risk List")
    st.dataframe(df.head(top_n))
    st.caption("Tip: Export this subset to CRM for a retention campaign.")
