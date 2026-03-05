"""
single_inference.py
Perform a single-point assessment of burnout risk using specific parameters.
"""

import argparse
import pandas as pd
import joblib
import numpy as np
from feature_engineering import extract_features

RISK_MAP = {0: "🟢 Low Risk", 1: "🟡 Medium Risk", 2: "🔴 High Risk"}

def get_single_assessment(eda, hr, acc, sleep_stage):
    # Load model
    model = joblib.load("model/burnout_model.pkl")
    
    # Create a dummy window of 500 identical samples to satisfy the feature engineering window requirements
    # and extract representative features for that steady-state sensor value.
    data = {
        "EDA": [eda] * 500,
        "HR": [hr] * 500,
        "ACC": [acc] * 500,
        "sleep_stage": [sleep_stage] * 500
    }
    df_window = pd.DataFrame(data)
    
    # Extract features
    features = extract_features(df_window)
    
    # Predict
    pred = model.predict(features)[0]
    prob = model.predict_proba(features)[0]
    
    return pred, prob

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Single-point Burnout Inference")
    parser.add_argument("--eda", type=float, required=True, help="EDA level (e.g., 0.1 to 1.5)")
    parser.add_argument("--hr", type=float, required=True, help="Heart Rate (e.g., 60 to 120)")
    parser.add_argument("--acc", type=float, required=True, help="Accelerometer mean (e.g., 0.1 to 1.0)")
    parser.add_argument("--sleep", type=str, default="Light", choices=["Wake", "Light", "Deep", "REM"], help="Current sleep stage")
    
    args = parser.parse_args()
    
    try:
        label, probabilities = get_single_assessment(args.eda, args.hr, args.acc, args.sleep)
        
        print("\n" + "="*30)
        print(f"ASSESSMENT: {RISK_MAP[label]}")
        print("="*30)
        print(f"Confidence Scores:")
        for idx, p in enumerate(probabilities):
            print(f" - {RISK_MAP[idx]:<15}: {p*100:>5.1f}%")
        print("="*30)
        
    except FileNotFoundError:
        print("❌ Error: Model file 'model/burnout_model.pkl' not found. Run train.py first.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
