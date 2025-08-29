<details>
  <summary><b>Table of Contents</b></summary>

- [Why this exists](#-why-this-exists)
- [Features](#-features)
- [Repository layout](#-repository-layout)
- [Quickstart](#-quickstart)
- [Train the model](#-train-the-model)
- [Run the API](#-run-the-api)
- [Use the Streamlit UI](#-use-the-streamlit-ui)
- [API contract](#-api-contract)
- [One-slide business summary](#-one-slide-business-summary)
- [Troubleshooting](#-troubleshooting)
- [Makefile](#-makefile)
- [Notes](#-notes)

</details>


💡 Why this exists

Predict which customers will churn in the next 30 days and rank them by risk so marketing can target the top-N with retention offers.

✅ Features

End-to-end local demo: prepare → train → serve → score.

FastAPI endpoint: POST /predict returns churn probabilities.

Streamlit UI: upload CSV → sort by churn_probability → export.

Reproducible training with printed Accuracy / Precision / Recall / F1.

Optional data drift report (Evidently) for show-and-tell.

🗂 Repository layout
churn-demo/
├─ data/
│  ├─ telco_raw.csv                # IBM Telco raw CSV
│  ├─ telco_train.csv              # prepared training data
│  ├─ telco_scoring_sample.csv     # sample for live scoring (no Churn column)
├─ models/
│  ├─ model.joblib                 # trained classifier
│  ├─ preprocessor.joblib          # fitted ColumnTransformer
├─ api/
│  ├─ main.py                      # FastAPI app (POST /predict)
│  ├─ schema.py                    # (optional) pydantic models
├─ app/
│  ├─ streamlit_app.py             # simple UI for demo
├─ train/
│  ├─ prepare_telco.py             # makes train + scoring files
│  ├─ train.py                     # trains model + prints metrics
│  ├─ utils.py                     # (optional) helpers
├─ reports/
│  ├─ drift_report.html            # (optional) Evidently report
├─ test.py                         # quick sanity checks
├─ requirements.txt
├─ README.md

[↑ Back to top](#-table-of-contents)

🚀 Quickstart
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt


Place dataset at:

data/telco_raw.csv


Prepare training + scoring files:

python train/prepare_telco.py


Optional sanity check:

python test.py

🧪 Train the model
python train/train.py


Artifacts saved to:

models/preprocessor.joblib
models/model.joblib


Re-train from scratch:

# macOS/Linux
rm -rf models && mkdir models
# Windows (PowerShell)
rmdir /s /q models; mkdir models
python train/train.py

📡 Run the API
uvicorn api.main:app --reload --port 8000
# Docs: http://localhost:8000/docs

🖥️ Use the Streamlit UI
streamlit run app/streamlit_app.py
# Usually opens http://localhost:8501


Upload data/telco_scoring_sample.csv (same columns, no Churn).

Click Score → see ranked churn probabilities.

Export table if needed (e.g. to CRM).

🔐 API contract

Endpoint

POST http://localhost:8000/predict


Request

{
  "records": [
    {
      "customerID": "7590-VHVEG",
      "gender": "Female",
      "SeniorCitizen": 0,
      "Partner": "Yes",
      "Dependents": "No",
      "tenure": 1,
      "PhoneService": "No",
      "MultipleLines": "No phone service",
      "InternetService": "DSL",
      "OnlineSecurity": "No",
      "OnlineBackup": "Yes",
      "DeviceProtection": "No",
      "TechSupport": "No",
      "StreamingTV": "No",
      "StreamingMovies": "No",
      "Contract": "Month-to-month",
      "PaperlessBilling": "Yes",
      "PaymentMethod": "Electronic check",
      "MonthlyCharges": 29.85,
      "TotalCharges": 29.85
    }
  ]
}


Response

{ "probabilities": [0.4123] }

🧠 One-slide business summary

Goal: Identify churners → target offers → reduce churn.

Approach: Logistic Regression with probabilities for ranking.

Key metrics: Recall & Precision (optimize retention ROI).

Integration idea: Weekly scoring → CRM → campaign → retraining loop.

🛠 Troubleshooting

JSON decode error in Streamlit → ensure API is running (http://localhost:8000/docs).

422 errors → check CSV schema (must match, no Churn column).

Model not found → train first (python train/train.py).

Port conflicts → run API on --port 8100, Streamlit on --server.port 8601.

🧰 Makefile

Save this as Makefile in project root:

PY ?= python
UVICORN_PORT ?= 8000
STREAMLIT_PORT ?= 8501

.PHONY: help install prepare train retrain api ui test clean clean-win

help:
	@echo "Targets:"
	@echo "  install     - Install dependencies"
	@echo "  prepare     - Build training & scoring CSVs"
	@echo "  train       - Train model"
	@echo "  retrain     - Clean models/ and train from scratch"
	@echo "  api         - Run FastAPI on port $(UVICORN_PORT)"
	@echo "  ui          - Run Streamlit on port $(STREAMLIT_PORT)"
	@echo "  test        - Run sanity checks"
	@echo "  clean       - Remove __pycache__ and models/"
	@echo "  clean-win   - Windows-safe clean"

install:
	$(PY) -m pip install -r requirements.txt

prepare:
	$(PY) train/prepare_telco.py

train:
	$(PY) train/train.py

retrain:
	rm -rf models && mkdir -p models
	$(PY) train/train.py

api:
	uvicorn api.main:app --reload --port $(UVICORN_PORT)

ui:
	streamlit run app/streamlit_app.py --server.port $(STREAMLIT_PORT)

test:
	$(PY) test.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf models

clean-win:
	powershell -NoProfile -Command ^
	  "Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force; ^
	   if (Test-Path models) { Remove-Item models -Recurse -Force }"

Example usage
make install
make prepare
make train
make api
make ui

📝 Notes

schema.py optional for stronger API contracts.

drift_report.html optional if you want monitoring talk track.

Project designed for live demo simplicity (no Docker needed).

# Makefile
make install
make prepare
make train
make api        # opens http://localhost:8000/docs
make ui         # opens http://localhost:8501

[↑ Back to top](#-table-of-contents)
