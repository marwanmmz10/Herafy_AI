from fastapi import FastAPI
import joblib
import os
import pandas as pd
from pydantic import BaseModel

# --- PATH LOGIC ---
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
model_path = os.path.join(base_dir, 'models', 'herafy_fraud_model.pkl')

# 1. Load the pre-trained brain (Model)
model = joblib.load(model_path)

# 2. Initialize FastAPI
app = FastAPI(title="Herafy AI Immunity System")


# 3. Define the Input Format (What the Back-end will send)
class ReviewInput(BaseModel):
    rating_value: float
    text_length: int
    rating_deviation: float
    is_night_owl: int


@app.get("/")
def home():
    return {"message": "Herafy AI API is Running!"}


@app.post("/predict")
def predict_fraud(data: ReviewInput):
    # Convert input to DataFrame for the model
    input_data = pd.DataFrame([data.dict()])

    # Get Prediction (0 or 1)
    prediction = model.predict(input_data)[0]

    # Get Probability (How sure the AI is)
    probability = model.predict_proba(input_data).tolist()[0]

    return {
        "is_suspicious": bool(prediction),
        "confidence_score": max(probability),
        "status": "Flagged" if prediction else "Clear"
    }

# To run this: py -m uvicorn src.main_api:app --reload