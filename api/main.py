# FastAPI app (predict)
from fastapi import FastAPI
import pandas as pd
import joblib
import json
from .schema import PredictRequest, PredictResponse
from .inference_preprocess import preprocess_inference

app = FastAPI(title="Churn Prediction API")

xgb_pipe = joblib.load("models/xgb_pipeline.joblib")
with open("models/xgb_threshold.json") as f:
    xgb_threshold = json.load(f)["best_threshold"]



@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    df = pd.DataFrame(req.records)
    df = preprocess_inference(df)
    proba = xgb_pipe.predict_proba(df)[:, 1].tolist()
    # Apply threshold to get class predictions
    preds = [int(p >= xgb_threshold) for p in proba]
    return PredictResponse(probabilities=proba, predictions=preds)

    
@app.get("/")
def root():
    return {"status": "ok", "service": "churn-api", "endpoints": ["/predict", "/docs"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)