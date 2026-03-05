import pandas as pd
import numpy as np

def compute_hrv_rmssd(rr_intervals):
    diff = np.diff(rr_intervals)
    return np.sqrt(np.mean(diff**2))

def extract_features(df):
    features = {}

    # ---- STRESS FEATURES ----
    features['mean_eda'] = df['EDA'].mean()
    features['eda_std'] = df['EDA'].std()
    features['stress_peak_count'] = (df['EDA'] > df['EDA'].mean() + df['EDA'].std()).sum()

    # ---- HEART RATE FEATURES ----
    features['mean_hr'] = df['HR'].mean()
    features['resting_hr'] = df['HR'].nsmallest(50).mean()  # true resting HR

    # Simulated RR intervals from HR
    rr_intervals = 60 / df['HR']
    features['hrv_rmssd'] = compute_hrv_rmssd(rr_intervals)

    # ---- ACTIVITY LOAD ----
    features['acc_mean'] = df['ACC'].mean()
    features['acc_variance'] = df['ACC'].var()

    # ---- SLEEP FEATURES ----
    if 'sleep_stage' in df.columns:
        total_sleep = len(df[df['sleep_stage'] != 'Wake'])
        rem_sleep = len(df[df['sleep_stage'] == 'REM'])
        features['sleep_efficiency'] = total_sleep / len(df)
        features['rem_ratio'] = rem_sleep / total_sleep if total_sleep > 0 else 0
    else:
        # Proxy: estimate rest periods using low accelerometer movement
        stillness_threshold = df['ACC'].mean() * 0.5
        still_periods = (df['ACC'] < stillness_threshold).sum()
        features['sleep_efficiency'] = still_periods / len(df)
        features['rem_ratio'] = 0.0  # cannot estimate without sleep stage labels

    return pd.DataFrame([features])