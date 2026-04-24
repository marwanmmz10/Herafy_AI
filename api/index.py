from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import os

# Create the FastAPI app instance
app = FastAPI()

# --- Step 1: Load the Trained Model ---
# We load the .pkl file which contains the "intelligence" of our Random Forest model
model_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'herafy_fraud_model.pkl')
model = joblib.load(model_path)

# --- Step 2: Define Input Data Structure ---
# This class defines what data the Backend should send in the JSON request
class ReviewData(BaseModel):
    rating_value: float
    text_length: int
    rating_deviation: float
    is_night_owl: int

@app.get("/")
def home():
    return {"message": "Herafy AI API is Running!"}

@app.post("/predict")
def predict(data: ReviewData):
    # --- Step 3: Prepare Data for Prediction ---
    # Convert incoming JSON data into a format (DataFrame) the model understands
    input_df = pd.DataFrame([{
        'rating_value': data.rating_value,
        'text_length': data.text_length,
        'rating_deviation': data.rating_deviation,
        'is_night_owl': data.is_night_owl
    }])

    # --- Step 4: Generate Prediction and Confidence ---
    # prediction: 0 (Normal) or 1 (Suspicious)
    prediction = model.predict(input_df)[0]
    # confidence: The probability percentage calculated by the model
    confidence_score = model.predict_proba(input_df)[0][1] * 100

    # --- Step 5: Build Arabic Reasons (Business Logic) ---
    # We collect suspicious patterns found in the data
    reasons_list = []

    # Check for short text with high ratings
    if data.text_length < 5 and data.rating_value == 5:
        reasons_list.append("نص التقييم قصير جداً أو غير موجود مع تقييم مرتفع")

    # Check for significant rating deviation, excluding the first-review case (deviation = 5)
    if data.rating_deviation > 2.0 and data.rating_deviation < 4.9:
        reasons_list.append("التقييم يختلف بشكل كبير عن متوسط تقييمات الفني")

    # Check for reviews submitted during late-night hours
    if data.is_night_owl == 1:
        reasons_list.append("تم إرسال التقييم في وقت متأخر جداً من الليل (وقت مريب)")

    # --- Step 6: Format Reasons into a Single String ---
    # If patterns are found, join them with a comma; otherwise, provide a default message
    if reasons_list:
        reasons_string = "، ".join(reasons_list)
    else:
        reasons_string = "لا توجد أنماط مشبوهة واضحة"

    # --- Step 7: Return the Final Response ---
    # Keys are in English for the Backend developer, values are in Arabic for the App UI
    return {
        "is_suspicious": bool(prediction),
        "confidence_score": round(float(confidence_score), 2),
        "status": "مشبوه" if prediction else "سليم",
        "reasons": reasons_string
    }