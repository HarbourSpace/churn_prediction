import pandas as pd
import joblib
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

from utils import TELCO_DROP_COLS, NUM_DTYPES


# --- Load training data ---
df = pd.read_csv("data/telco_train.csv")

if "Churn" not in df.columns:
    raise ValueError("Expected 'Churn' column in data/telco_train.csv")

y = df["Churn"]
X = df.drop(columns=TELCO_DROP_COLS, errors="ignore")

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
num_cols = X.select_dtypes(include=NUM_DTYPES).columns.tolist()
cat_cols = [c for c in X_train.columns if c not in num_cols]

preprocessor = ColumnTransformer([
    ("num", StandardScaler(), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])

# --- Classifier ---
clf = LogisticRegression(max_iter=1000, class_weight="balanced")

pipe = Pipeline(steps=[
    ("prep", preprocessor),
    ("clf", clf),
])

# --- Fit model ---
pipe.fit(X_train, y_train)

# --- Evaluate on validation set ---
y_pred = pipe.predict(X_val)
acc = accuracy_score(y_val, y_pred)
prec = precision_score(y_val, y_pred)
rec = recall_score(y_val, y_pred)
f1 = f1_score(y_val, y_pred)

print("\n📊 Validation Metrics:")
print(f"  Accuracy : {acc:.3f}")
print(f"  Precision: {prec:.3f}")
print(f"  Recall   : {rec:.3f}")
print(f"  F1-score : {f1:.3f}")

# --- Save artifacts ---
prep = pipe.named_steps["prep"]
model = pipe.named_steps["clf"]
joblib.dump(prep, "models/preprocessor.joblib")
joblib.dump(model, "models/model.joblib")
print("\n✅ Saved models/preprocessor.joblib and models/model.joblib")
