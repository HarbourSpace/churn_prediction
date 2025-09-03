# Pydantic request/response models

# api/schema.py
from pydantic import BaseModel
from typing import List, Dict, Any

class PredictRequest(BaseModel):
    records: List[Dict[str, Any]]  # list of row dicts

class PredictResponse(BaseModel):
    probabilities: List[float]
    predictions: List[int]  # 0 or 1 for each record
    