import pandas as pd
import numpy as np

def preprocess_inference(df: pd.DataFrame) -> pd.DataFrame:
    # --- Basic cleaning: TotalCharges ---
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)

    # --- Collapse "No internet service" / "No phone service" ---
    internet_service_no_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "MultipleLines"
    ]
    for c in internet_service_no_cols:
        if c in df.columns:
            df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

    # --- Yes/No → 1/0 ---
    yes_no_cols = [
        "Partner", "Dependents", "PhoneService", "PaperlessBilling",
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "MultipleLines"
    ]
    for c in yes_no_cols:
        if c in df.columns:
            df[c] = df[c].map({"Yes": 1, "No": 0}).fillna(0).astype(int)

    # --- Feature engineering ---
    if "tenure" in df.columns:
        tenure_nonzero = df["tenure"].replace(0, 1)

        if "MonthlyCharges" in df.columns:
            df["TotalSpend"] = df["MonthlyCharges"] * df["tenure"]

        if "TotalCharges" in df.columns:
            df["AvgChargesPerMonth"] = df["TotalCharges"] / tenure_nonzero

        df["tenure_group"] = pd.cut(
            df["tenure"],
            bins=[-0.1, 12, 24, 48, 60, np.inf],
            labels=["0-12", "13-24", "25-48", "49-60", "61+"]
        )

    return df
