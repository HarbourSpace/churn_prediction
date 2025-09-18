import pandas as pd
import numpy as np
import joblib
import json
import os

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline as SkPipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, average_precision_score, classification_report
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
from xgboost import XGBClassifier


from utils import TELCO_DROP_COLS, NUM_DTYPES


# --- Load training data ---
df = pd.read_csv("data/telco_train.csv")

cat_cols = df.select_dtypes(include='object').columns
for col in cat_cols:
    df[col] = df[col].astype('category')

if "Churn" not in df.columns:
    raise ValueError("Expected 'Churn' column in data/telco_train.csv")

y = df["Churn"]
X = df.drop(columns=["Churn"], errors="ignore")

# Early sanity check
unique_classes = sorted(y.unique().tolist())
print("Training classes found:", unique_classes)
if len(unique_classes) < 2:
    raise ValueError(
        f"Training data has a single class {unique_classes}. "
        f"Re-run `python train/prepare_telco.py` and ensure stratification worked."
    )

# --- Split into train/validation ---
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# --- Define preprocessing ---
num_cols = X_train.select_dtypes(include=NUM_DTYPES).columns.tolist()
cat_cols = [c for c in X_train.columns if c not in num_cols]

preprocessor_logreg = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), num_cols),
        ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
    ],
    remainder='passthrough'
)

# --- Baseline model: Logistic Regression + SMOTE ---
print("\n=== Baseline: Logistic Regression + SMOTE (not saved) ===")

log_clf = LogisticRegression(max_iter=1000)

log_pipe = ImbPipeline([
    ("prep", preprocessor_logreg),
    ("smote", SMOTE(random_state=42)),
    ("clf", log_clf),
])

# --- Fit model ---
log_pipe.fit(X_train, y_train)
# --- Evaluate on validation set ---
y_log_pred = log_pipe.predict(X_val) # default threshold 0.5
y_log_proba = log_pipe.predict_proba(X_val)[:, 1]

log_acc = accuracy_score(y_val, y_log_pred)
log_prec = precision_score(y_val, y_log_pred, zero_division=0)
log_rec = recall_score(y_val, y_log_pred, zero_division=0)
log_f1 = f1_score(y_val, y_log_pred, zero_division=0)
log_roc_auc = roc_auc_score(y_val, y_log_proba)
log_avg_prec = average_precision_score(y_val, y_log_proba)

print("\nValidation Metrics @0.50:")
print(f"  Accuracy : {log_acc:.3f}")
print(f"  Precision: {log_prec:.3f}")
print(f"  Recall   : {log_rec:.3f}")
print(f"  F1-score : {log_f1:.3f}")
print(f"  ROC AUC  : {log_roc_auc:.3f}")
print(f"  Avg Prec.: {log_avg_prec:.3f}")
print("\nClassification Report:")
print(classification_report(y_val, y_log_pred, zero_division=0, digits=3))

# --- Threshold tuning for better F1 for baseline ---
ths = np.linspace(0.05, 0.95, 19)
f1s = []
for t in ths:
    y_hat = (y_log_proba >= t).astype(int)
    f1s.append(f1_score(y_val, y_hat, zero_division=0))
best_idx = int(np.argmax(f1s))
best_t = float(ths[best_idx])
best_f1 = float(f1s[best_idx])
y_hat_best = (y_log_proba >= best_t).astype(int)

print(f"\n\nBaseline threshold tuning:")
print(f"  Best F1 at threshold={best_t:.2f}: F1={best_f1:.3f}")
print(f"  Precision: {precision_score(y_val, y_hat_best, zero_division=0):.3f}")
print(f"  Recall   : {recall_score(y_val, y_hat_best, zero_division=0):.3f}")
print(f"\nClassification Report:")
print(classification_report(y_val, y_hat_best, zero_division=0, digits=3))

print("Note: Baseline model is NOT saved.\n")


# --- Final model: XGBoost (no SMOTE, use weights) ---
print("\n\n\n\n""=== Final: XGBoost (saved) ===")

n_pos = int((y_train == 1).sum())
n_neg = int((y_train == 0).sum())
spw = (n_neg / n_pos) if n_pos > 0 else 1.0  # imbalance handling

xgb = XGBClassifier(
    n_estimators=1000,
    max_depth=3,
    learning_rate=0.01,
    tree_method="hist",
    scale_pos_weight=spw,   # keep this
    eval_metric=["logloss"],
    random_state=42,
    enable_categorical=True,
)

# For tree-based models, no need to scale numerics
preprocessor_xgb = ColumnTransformer(
    transformers=[
        # Pass all columns through; XGBoost will handle them natively
        ("pass", "passthrough", X_train.columns)
    ]
)

xgb_pipe = SkPipeline([
    #("prep", preprocessor_xgb),
    ("clf", xgb),
])

# --- Fit model ---
xgb_pipe.fit(X_train, y_train, clf__verbose=True, clf__eval_set=[(X_val, y_val)])

# --- Evaluate on validation set ---
y_xgb_pred = xgb_pipe.predict(X_val) # default threshold 0.5
y_xgb_proba = xgb_pipe.predict_proba(X_val)[:, 1]

xgb_acc = accuracy_score(y_val, y_xgb_pred)
xgb_prec = precision_score(y_val, y_xgb_pred, zero_division=0)
xgb_rec = recall_score(y_val, y_xgb_pred, zero_division=0)
xgb_f1 = f1_score(y_val, y_xgb_pred, zero_division=0)
xgb_roc_auc = roc_auc_score(y_val, y_xgb_proba)
xgb_avg_prec = average_precision_score(y_val, y_xgb_proba)

print("\nValidation Metrics @0.50:")
print(f"  Accuracy : {xgb_acc:.3f}")
print(f"  Precision: {xgb_prec:.3f}")
print(f"  Recall   : {xgb_rec:.3f}")
print(f"  F1-score : {xgb_f1:.3f}")
print(f"  ROC AUC  : {xgb_roc_auc:.3f}")
print(f"  Avg Prec.: {xgb_avg_prec:.3f}")
print("\nClassification Report:")
print(classification_report(y_val, y_xgb_pred, zero_division=0, digits=3))

# --- Treshold tuning for better F1 ---
ths = np.linspace(0.05, 0.95, 19)
f1s = []
for t in ths:
    y_hat = (y_xgb_proba >= t).astype(int)
    f1s.append(f1_score(y_val, y_hat, zero_division=0))
best_idx = int(np.argmax(f1s))
best_t = float(ths[best_idx])
best_f1 = float(f1s[best_idx])
y_hat_best = (y_xgb_proba >= best_t).astype(int)

print(f"\n\nXGBoost threshold tuning:")
print(f"  Best F1 at threshold={best_t:.2f}: F1={best_f1:.3f}")
print(f"  Precision: {precision_score(y_val, y_hat_best, zero_division=0):.3f}")
print(f"  Recall   : {recall_score(y_val, y_hat_best, zero_division=0):.3f}")
print(f"\nClassification Report:")
print(classification_report(y_val, y_hat_best, zero_division=0, digits=3))



# --- Save final model and artifacts ---
os.makedirs("models", exist_ok=True)
joblib.dump(xgb_pipe, "models/xgb_pipeline.joblib")

with open("models/xgb_threshold.json", "w") as f:
    json.dump({"best_threshold": best_t}, f)

print("\n✅ Saved models/xgb_pipeline.joblib and models/xgb_threshold.json")
print("ℹ️  Baseline model not saved.")






