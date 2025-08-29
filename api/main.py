# FastAPI app (predict)
from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from .schema import PredictRequest, PredictResponse

app = FastAPI(title="Churn Prediction API")

preprocessor = joblib.load("models/preprocessor.joblib")
model = joblib.load("models/model.joblib")


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    df = pd.DataFrame(req.records)
    X = preprocessor.transform(df)
    proba = model.predict_proba(X)[:, 1].tolist()
    return PredictResponse(probabilities=proba)
@app.get("/")
def root():
    return {"status": "ok", "service": "churn-api", "endpoints": ["/predict", "/docs"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)