# Pydantic request/response models

# api/schema.py
from pydantic import BaseModel, validator
from typing import List, Dict, Any, Optional
import re

class PredictRequest(BaseModel):
    records: List[Dict[str, Any]]  # list of row dicts

class ChurnSummary(BaseModel):
    total_customers: int
    churn_count: int
    no_churn_count: int
    churn_percentage: float
    no_churn_percentage: float

class PredictResponse(BaseModel):
    probabilities: List[float]
    predictions: List[int]
    summary: ChurnSummary

class EmailRequest(BaseModel):
    recipient_email: str
    results_csv_path: Optional[str] = None
    
    @validator('recipient_email')
    def validate_email(cls, v):
        # Basic email validation regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v
    