# test.py
from pathlib import Path
import pandas as pd

DATA_DIR = Path("data")
FILES = {
    "raw": DATA_DIR / "telco_raw.csv",
    "train": DATA_DIR / "telco_train.csv",
    "score": DATA_DIR / "telco_scoring_sample.csv",
}

def show_basic(name: str, path: Path, check_churn: bool = True):
    if not path.exists():
        print(f"[{name}] MISSING -> {path}")
        return

    df = pd.read_csv(path)
    print(f"\n[{name}] OK -> {path}")
    print(f"  rows={len(df):,}  cols={len(df.columns)}")
    print(f"  columns: {list(df.columns)[:12]}{' ...' if len(df.columns) > 12 else ''}")

    if check_churn:
        if "Churn" in df.columns:
            vc = df["Churn"].value_counts(dropna=False)
            print("  'Churn' value counts:")
            print(" ", vc.to_dict())
            # Normalize to 0/1 if looks like strings
            if df["Churn"].dtype == object:
                norm = df["Churn"].astype(str).str.strip().str.lower()
                print("  normalized churn counts (yes/no):", norm.value_counts(dropna=False).to_dict())
            # Class sanity
            uniq = sorted(pd.unique(df["Churn"]))
            print("  unique values in Churn:", uniq)
            if len(uniq) < 2:
                print("  ❗ PROBLEM: Only one class present in this file.")
        else:
            print("  ❗ WARNING: No 'Churn' column found in this file.")

def main():
    print("== Checking data files ==")
    show_basic("raw", FILES["raw"], check_churn=True)
    show_basic("train", FILES["train"], check_churn=True)

    # scoring sample should NOT have Churn
    if FILES["score"].exists():
        df_score = pd.read_csv(FILES["score"])
        print(f"\n[score] OK -> {FILES['score']}")
        print(f"  rows={len(df_score):,}  cols={len(df_score.columns)}")
        has_churn = "Churn" in df_score.columns
        print(f"  contains 'Churn' column? {has_churn}")
        if has_churn:
            print("  ❗ PROBLEM: scoring sample must NOT include 'Churn'. Drop it before scoring.")
        else:
            print("  ✓ scoring sample looks good (no target column).")
        print(f"  columns: {list(df_score.columns)[:12]}{' ...' if len(df_score.columns) > 12 else ''}")
    else:
        print(f"\n[score] MISSING -> {FILES['score']}")

    print("\n== Tips ==")
    print("- If TRAIN shows only one Churn class, re-run your prepare script with stratified split.")
    print("- If SCORE contains 'Churn', remove it for demo scoring.")
    print("- If RAW has only 'no' churn, download a standard IBM Telco CSV.")

if __name__ == "__main__":
    main()

    print("\n== Done ==")