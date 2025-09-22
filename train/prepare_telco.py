import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

RAW = Path("data/telco_raw.csv")
TRAIN_OUT = Path("data/telco_train.csv")
SCORE_SAMPLE_OUT = Path("data/telco_scoring_sample.csv")

def main():
    if not RAW.exists():
        raise FileNotFoundError(
            f"Could not find {RAW}. Please place the raw Telco CSV there and name it 'telco_raw.csv'."
        )

    df = pd.read_csv(RAW)
    # NOTE: DO NOT drop customerID here. Keep it for the scoring sample.

    # --- Basic cleaning: TotalCharges ---
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        before = len(df)
        df = df.dropna(subset=["TotalCharges"]).copy()
        after = len(df)
        print(f"Dropped {before - after} rows with missing TotalCharges.")
    else:
        print("Warning: 'TotalCharges' column not found in raw file.")

    # Normalize target Churn → 0/1
    if "Churn" in df.columns:
        df["Churn"] = (
            df["Churn"].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0})
        )
    else:
        raise ValueError("Column 'Churn' not found in raw dataset.")

    # Collapse "No internet service" → "No" for service-related cols to reduce cardinality
    internet_service_no_cols = [
        "OnlineSecurity", "OnlineBackup", "DeviceProtection",
        "TechSupport", "StreamingTV", "StreamingMovies", "MultipleLines"
    ]
    for c in internet_service_no_cols:
        if c in df.columns:
            df[c] = df[c].replace({"No internet service": "No", "No phone service": "No"})

    # Feature engineering
    if "tenure" in df.columns:
        tenure_nonzero = df["tenure"].replace(0, 1)
    else:
        raise ValueError("Column 'tenure' not found in raw dataset.")

    if "MonthlyCharges" in df.columns:
        df["TotalSpend"] = df["MonthlyCharges"] * df["tenure"]
    else:
        raise ValueError("Column 'MonthlyCharges' not found in raw dataset.")

    if "TotalCharges" in df.columns:
        df["AvgChargesPerMonth"] = df["TotalCharges"] / tenure_nonzero

    df["tenure_group"] = pd.cut(
        df["tenure"],
        bins=[-0.1, 12, 24, 48, 60, np.inf],
        labels=["0-12", "13-24", "25-48", "49-60", "61+"]
    ).astype('category')

    object_cols = df.select_dtypes(include=['object']).columns
    for c in object_cols:
        df[c] = df[c].astype('category')

    counts = df["Churn"].value_counts(dropna=False)
    print("Class distribution (overall):")
    print(counts)

    # Stratified split
    train_df, score_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["Churn"]
    )

    # Now, drop customerID from the training data
    train_df = train_df.drop(columns=["customerID"], errors="ignore")

    # The scoring sample should NOT include the target column, but MUST include the customerID
    score_no_target = score_df.drop(columns=["Churn"], errors="ignore")

    # Optionally trim scoring sample to ~200 rows
    score_no_target = score_no_target.head(200).copy()

    TRAIN_OUT.parent.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(TRAIN_OUT, index=False)
    score_no_target.to_csv(SCORE_SAMPLE_OUT, index=False)

    print(f"Saved training set: {TRAIN_OUT} (rows={len(train_df)})")
    print("Training class distribution:")
    print(train_df["Churn"].value_counts())

    print(f"Saved scoring sample (no target): {SCORE_SAMPLE_OUT} (rows={len(score_no_target)})")
    print("Done.")

if __name__ == "__main__":
    main()