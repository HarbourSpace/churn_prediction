# -------- Config --------
PY ?= python
UVICORN_PORT ?= 8000
STREAMLIT_PORT ?= 8501
FRONTEND_PORT ?= 3000

# -------- Phony targets --------
.PHONY: help install prepare train retrain api ui frontend test baseline clean clean-win

help:
	@echo "Targets:"
	@echo "  install     - Install Python deps from requirements.txt"
	@echo "  prepare     - Build training & scoring CSVs"
	@echo "  train       - Train model (creates models/*.joblib)"
	@echo "  retrain     - Clean models/ and train from scratch"
	@echo "  baseline    - Create baseline data for drift detection"
	@echo "  api         - Run FastAPI (uvicorn) on port $(UVICORN_PORT)"
	@echo "  ui          - Run Streamlit UI on port $(STREAMLIT_PORT)"
	@echo "  frontend    - Run web frontend on port $(FRONTEND_PORT)"
	@echo "  test        - Sanity checks on CSVs"
	@echo "  clean       - Remove __pycache__ and models/"
	@echo "  clean-win   - Windows-safe clean using PowerShell"

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

baseline:
	$(PY) create_baseline.py

ui:
	streamlit run app/streamlit_app.py --server.port $(STREAMLIT_PORT)

frontend:
	cd telecom_churn_frontend && $(PY) -m http.server $(FRONTEND_PORT)

test:
	$(PY) test.py

# POSIX clean (macOS/Linux/Git Bash)
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf models

# PowerShell clean (use: `make clean-win` from PowerShell if needed)
clean-win:
	powershell -NoProfile -Command ^
	  "Get-ChildItem -Recurse -Directory -Filter __pycache__ | Remove-Item -Recurse -Force; ^
	   if (Test-Path models) { Remove-Item models -Recurse -Force }"
