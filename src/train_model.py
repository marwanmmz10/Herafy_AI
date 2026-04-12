import pandas as pd
import os
import joblib  # Library to save/load the trained model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# --- ROBUST PATH LOGIC ---
# Get the directory of the current script (Herafy_AI/src)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Get the base project directory (Herafy_AI)
base_dir = os.path.dirname(script_dir)


def train_herafy_model():
    # 1. Define Paths
    input_path = os.path.join(base_dir, 'data', 'herafy_with_features.csv')
    model_dir = os.path.join(base_dir, 'models')
    model_save_path = os.path.join(model_dir, 'herafy_fraud_model.pkl')

    # 2. Load the processed data
    if not os.path.exists(input_path):
        print(f"Error: Missing {input_path}. Please run feature_engine.py first.")
        return

    df = pd.read_csv(input_path)

    # 3. Feature Selection (X) and Target (y)
    # These are the 4 features that help the AI detect fraud patterns
    features = ['rating_value', 'text_length', 'rating_deviation', 'is_night_owl']
    X = df[features]

    # Target column: is_suspicious (True/False)
    y = df['is_suspicious']

    # 4. Split Data (80% Train, 20% Test)
    # We train on 80% and keep 20% to test if the model actually learned
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 5. Initialize & Train the Model
    # Random Forest is powerful and simple for this kind of tabular data
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 6. Evaluation - Testing the model on unseen data
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print("--- Model Training Result ---")
    print(f"Accuracy: {accuracy * 100:.2f}%")
    print("\nDetailed Performance Report:")
    print(classification_report(y_test, y_pred))

    # 7. Save the "Brain" of the AI
    # This .pkl file is what we will use later in the API
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, model_save_path)
    print(f"\nSuccess! Model saved at: {model_save_path}")


if __name__ == "__main__":
    train_herafy_model()