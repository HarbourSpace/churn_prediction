import pandas as pd
import numpy as np

def preprocess_inference(df: pd.DataFrame) -> pd.DataFrame:
    # Preprocess input DataFrame for inference.

    # Drop customerID, as it is not a feature for the model
    df.drop(columns=["customerID"], inplace=True, errors="ignore")

    # --- Basic cleaning: TotalCharges ---
    if "TotalCharges" in df.columns:
        # Coerce to numeric, which will turn invalid parsing into NaN
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        # Impute missing values with 0.
        # This should be consistent with the data preparation for training.
        df["TotalCharges"] = df["TotalCharges"].fillna(0)
    else:
        print("Warning: 'TotalCharges' column not found in raw data.")

    # --- Collapse "No internet service" / "No phone service" ---
    internet_service_no_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "MultipleLines"
    ]
    for c in internet_service_no_cols:
        if c in df.columns:
            df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

    # --- Feature engineering ---
    if "tenure" in df.columns:
        tenure_nonzero = df["tenure"].replace(0, 1)
        if "MonthlyCharges" in df.columns:
            df["TotalSpend"] = df["MonthlyCharges"] * df["tenure"]
        if "TotalCharges" in df.columns:
            df["AvgChargesPerMonth"] = df["TotalCharges"] / tenure_nonzero

        # Create tenure bins and explicitly set as 'category' dtype
        df["tenure_group"] = pd.cut(
            df["tenure"],
            bins=[-0.1, 12, 24, 48, 60, np.inf],
            labels=["0-12", "13-24", "25-48", "49-60", "61+"]
        ).astype('category')
    
    # --- Convert all remaining object columns to 'category' dtype ---
    object_cols = df.select_dtypes(include=['object']).columns
    for c in object_cols:
        df[c] = df[c].astype('category')

    return df 

