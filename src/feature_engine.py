import pandas as pd
import numpy as np
import os

# --- Step 1: File Path Setup ---
# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
# Move up to the project root directory
base_dir = os.path.dirname(script_dir)
# Define input and output file paths
input_path = os.path.join(base_dir, 'data', 'herafy_reviews.csv')
output_path = os.path.join(base_dir, 'data', 'herafy_with_features.csv')

# --- Step 2: Load Data ---
# Read the raw CSV data into a Pandas DataFrame
df = pd.read_csv(input_path)

# --- Step 3: Feature Engineering ---

# A. Calculate Text Length
# If the review text is empty, replace it with an empty string, then count characters
df['text_length'] = df['review_text'].fillna('').apply(lambda x: len(str(x)))

# B. Calculate Rating Deviation
# Calculate the average rating for each technician
tech_mean = df.groupby('technician_id')['rating_value'].transform('mean')
# Calculate the absolute difference between the current rating and the average
df['rating_deviation'] = np.abs(df['rating_value'] - tech_mean)

# C. Detect Night Owl behavior (1 AM to 5 AM)
# Convert the created_at column to a special time format
df['created_at'] = pd.to_datetime(df['created_at'])
# Check if the hour is between 1 and 5 (inclusive) and convert to 0 or 1
df['is_night_owl'] = df['created_at'].dt.hour.between(1, 5).astype(int)

# --- Step 4: Fraud Scoring Logic ---

# Initialize a fraud_score column starting at 0
df['fraud_score'] = 0

# Rule 1: Very short text (less than 5 chars) with a perfect 5-star rating
short_text_rule = (df['rating_value'] == 5) & (df['text_length'] < 5)
df.loc[short_text_rule, 'fraud_score'] += 50

# Rule 2: Night owl reviews (suspicious timing)
night_owl_rule = (df['is_night_owl'] == 1)
df.loc[night_owl_rule, 'fraud_score'] += 30

# Rule 3: High Rating Deviation (excluding the first review case)
# If deviation > 2.0 but NOT equal to 5.0 (the first review indicator)
# We use < 4.9 to filter out cases where the deviation is 5.0
deviation_rule = (df['rating_deviation'] > 2.0) & (df['rating_deviation'] < 4.9)
df.loc[deviation_rule, 'fraud_score'] += 20

# --- Step 5: Final Labeling ---
# If total fraud_score is 50 or more, mark the review as suspicious
df['is_suspicious'] = df['fraud_score'] >= 50

# --- Step 6: Save Processed Data ---
# Save the new table with all features and labels to a new CSV
df.to_csv(output_path, index=False)

print(f"Feature engineering complete! Data saved to {output_path}")