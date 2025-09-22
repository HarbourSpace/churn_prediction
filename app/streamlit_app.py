import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Churn Demo", layout="wide")
st.title("📉 Telecom Churn Prediction — Demo")

uploaded = st.file_uploader("Upload CSV of active customers", type=["csv"])
top_n = st.slider("Show top-N highest risk customers", 5, 200, 50)

if st.button("Score") and uploaded:
    # Use the /predict_churn endpoint with file upload
    files = {"file": uploaded.getvalue()}
    params = {"k_value": top_n}
    res = requests.post("http://localhost:8000/predict_churn", files=files, params=params)
    result = res.json()
    
    # Get the data from the response (already includes predictions)
    df = pd.DataFrame(result["data"])
    
    # Display summary metrics
    summary = result["summary"]
    st.subheader("📊 Summary Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Customers", summary["total_customers"])
    with col2:
        st.metric("Predicted to Churn", 
                 f"{summary['churn_count']} ({summary['churn_percentage']}%)",
                 delta=f"{summary['churn_percentage']}%")
    with col3:
        st.metric("Predicted to Stay", 
                 f"{summary['no_churn_count']} ({summary['no_churn_percentage']}%)",
                 delta=f"{summary['no_churn_percentage']}%")
    
    # Display ranked risk list
    st.subheader("🎯 Ranked Risk List")
    df = df.sort_values("churn_probability", ascending=False)
    st.dataframe(df.head(top_n))
    st.caption("Tip: Export this subset to CRM for a retention campaign.")

    # Download buttons
    all_csv = df.to_csv(index=False).encode("utf-8")
    top_csv = df.head(top_n).to_csv(index=False).encode("utf-8")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("⬇️ Download ALL results (CSV)", 
                         all_csv, "churn_scores_all.csv", "text/csv")
    with col2:
        st.download_button(f"⬇️ Download TOP {top_n} (CSV)", 
                         top_csv, f"churn_scores_top_{top_n}.csv", "text/csv")
