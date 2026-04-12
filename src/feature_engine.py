import pandas as pd
import numpy as np
import os
from datetime import datetime


# 1. Get the directory where this script (feature_engine.py) is located (Herafy_AI/src)
script_dir = os.path.dirname(os.path.abspath(__file__))

# 2. Get the main project folder (Herafy_AI)
base_dir = os.path.dirname(script_dir)


def build_feature_pipeline():
    # 3. Define Final Paths (Everything is now inside the 'data' folder)
    input_path = os.path.join(base_dir, 'data', 'herafy_reviews.csv')
    output_path = os.path.join(base_dir, 'data', 'herafy_with_features.csv')

    print(f"DEBUG: Looking for input file at: {input_path}")

    # 4. Load the raw data
    try:
        df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"CRITICAL ERROR: Could not find {input_path}")
        print("Please ensure you ran generate_data.py first and the file is in the 'data' folder.")
        return

    # --- STAGE 1: FEATURE ENGINEERING ---

    # Feature 1: Text Length (Fraudulent reviews are often empty or very short)
    df['text_length'] = df['review_text'].fillna('').apply(lambda x: len(str(x)))

    # Feature 2: Rating Deviation (Is this rating very different from the tech's average?)
    tech_mean = df.groupby('technician_id')['rating_value'].transform('mean')
    df['rating_deviation'] = np.abs(df['rating_value'] - tech_mean)

    # Feature 3: Device Review Count (Velocity check: how many times this device was used)
    df['device_review_count'] = df.groupby('device_id')['device_id'].transform('count')

    # Feature 4: Night Owl (Is the review posted between 1 AM and 5 AM?)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['is_night_owl'] = df['created_at'].dt.hour.between(1, 5).astype(int)

    # --- STAGE 2: RULE-BASED DETECTION (FRAUD SCORING) ---

    df['fraud_score'] = 0

    # Rule A: High risk if service was not completed
    df.loc[df['service_status'] != 'completed', 'fraud_score'] += 100

    # Rule B: High risk if device is used too frequently
    df.loc[df['device_review_count'] > 2, 'fraud_score'] += 45

    # Rule C: Moderate risk if posted at suspicious hours (Night Owl)
    df.loc[df['is_night_owl'] == 1, 'fraud_score'] += 20

    # Rule D: Moderate risk for 5-star ratings with no text
    short_text_rule = (df['rating_value'] == 5) & (df['text_length'] < 5)
    df.loc[short_text_rule, 'fraud_score'] += 30

    # Final Classification: Threshold = 50
    df['is_suspicious'] = df['fraud_score'] >= 50

    # --- SAVE PROCESSED DATA ---
    # Ensure 'data' directory exists (double check)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_csv(output_path, index=False)
    print(f"Success! Featured data saved to: {output_path}")

    # Optional: Print some results to the console
    print("\n--- Quick Fraud Check (First 5 Suspicious) ---")
    print(df[df['is_suspicious'] == True][['review_id', 'fraud_score', 'is_suspicious']].head())


if __name__ == "__main__":
    build_feature_pipeline()