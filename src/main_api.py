from fastapi import FastAPI
import joblib
import os
import pandas as pd
from pydantic import BaseModel
from typing import List

# --- PATH LOGIC ---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
model_path = os.path.join(base_dir, 'models', 'herafy_fraud_model.pkl')

# 1. Load the model
model = joblib.load(model_path)

app = FastAPI(title="Herafy AI Immunity System")


class ReviewInput(BaseModel):
    rating_value: float
    text_length: int
    rating_deviation: float
    is_night_owl: int


@app.post("/predict")
def predict_fraud(data: ReviewInput):
    # Convert input to DataFrame
    input_df = pd.DataFrame([data.dict()])

    # Get Prediction & Probability
    prediction = model.predict(input_df)[0]
    probability = model.predict_proba(input_df).tolist()[0]
    confidence = max(probability)

    # --- REASON LOGIC (Explainable AI) ---
    reasons = []
    if data.is_night_owl == 1:
        reasons.append("Review posted at suspicious late-night hours (1AM-5AM).")
    if data.text_length < 10:
        reasons.append("Review text is too short or empty.")
    if data.rating_deviation > 2.0:
        reasons.append("Rating is significantly different from technician's average.")
    if data.rating_value == 5 and data.text_length < 5:
        reasons.append("High rating with no descriptive text (typical bot behavior).")

    # If it's not suspicious, clear the reasons
    final_reasons = reasons if prediction else ["No suspicious patterns detected."]

    return {
        "is_suspicious": bool(prediction),
        "confidence_score": round(confidence * 100, 2),  # Percentage
        "status": "Flagged" if prediction else "Clear",
        "reasons": final_reasons
    }