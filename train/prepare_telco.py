import pandas as pd
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

    # --- Basic cleaning specific to IBM Telco ---
    # Coerce TotalCharges to numeric and drop NAs (new customers often have NA)
    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
        before = len(df)
        df = df.dropna(subset=["TotalCharges"]).copy()
        after = len(df)
        print(f"Dropped {before - after} rows with missing TotalCharges.")

    # Normalize Churn to 0/1 if present
    if "Churn" in df.columns:
        df["Churn"] = (
            df["Churn"].astype(str).str.strip().str.lower().map({"yes": 1, "no": 0})
        )
    else:
        raise ValueError("Column 'Churn' not found in raw dataset.")

    # Quick sanity check
    counts = df["Churn"].value_counts(dropna=False)
    print("Class distribution (overall):")
    print(counts)

    # Stratified split so both classes appear in train
    train_df, score_df = train_test_split(
        df, test_size=0.2, random_state=42, stratify=df["Churn"]
    )

    # The scoring sample should NOT include the target column
    score_no_target = score_df.drop(columns=["Churn"])

    # Optionally trim scoring sample to ~200 rows for the live demo
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
