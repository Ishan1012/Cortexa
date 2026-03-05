"""
predict.py
Run inference on new wearable sensor data using the trained burnout model.

Usage:
    python predict.py --input new_sensor_data.csv
"""

import argparse
import pandas as pd
import joblib
from feature_engineering import extract_features

RISK_MAP = {0: "🟢 Low Risk", 1: "🟡 Medium Risk", 2: "🔴 High Risk"}

def predict(input_csv: str, window_size: int = 500):
    model = joblib.load("model/burnout_model.pkl")
    df = pd.read_csv(input_csv)

    if len(df) < window_size:
        print(f"⚠️  Input has only {len(df)} rows — need at least {window_size}.")
        return

    feature_list = []
    for i in range(0, len(df) - window_size, window_size):
        window = df.iloc[i:i + window_size]
        features = extract_features(window)
        feature_list.append(features)

    X = pd.concat(feature_list, ignore_index=True)
    preds = model.predict(X)
    probs = model.predict_proba(X)

    print(f"\n{'Window':<8} {'Prediction':<18} {'Probs (per class)':<18}")
    print("-" * 50)
    for idx, (p, prob) in enumerate(zip(preds, probs)):
        prob_str = " | ".join([f"{c}: {v*100:>.1f}%" for c, v in zip(model.classes_, prob)])
        print(f"{idx:<8} {RISK_MAP[p]:<18} {prob_str}")

    overall = max(set(preds.tolist()), key=preds.tolist().count)
    print(f"\n📊 Overall Assessment: {RISK_MAP[overall]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to input CSV with EDA, HR, ACC columns")
    parser.add_argument("--window", type=int, default=500, help="Window size (must match training)")
    args = parser.parse_args()
    predict(args.input, args.window)
