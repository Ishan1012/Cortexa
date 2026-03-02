"""
generate_data.py
Generates a synthetic merged_wearable_data.csv for training the burnout model.
Simulates three population profiles: healthy, moderate burnout, high burnout.
Run this ONCE before running train.py.
"""

import numpy as np
import pandas as pd

np.random.seed(42)

SAMPLES_PER_PROFILE = 50_000   # total rows per profile → 150k rows total
PROFILES = [
    {
        "name": "healthy",
        # Low EDA, lower resting HR, high HRV (implicitly captured via HR variability)
        "eda_mean": 0.2, "eda_std": 0.08,
        "hr_mean": 62,   "hr_std": 8,
        "acc_mean": 0.4, "acc_std": 0.15,
        "sleep_dist": {"Wake": 0.15, "Light": 0.45, "Deep": 0.25, "REM": 0.15},
    },
    {
        "name": "moderate_burnout",
        "eda_mean": 0.65, "eda_std": 0.15,
        "hr_mean": 85,    "hr_std": 10,
        "acc_mean": 0.5,  "acc_std": 0.2,
        "sleep_dist": {"Wake": 0.35, "Light": 0.45, "Deep": 0.10, "REM": 0.10},
    },
    {
        "name": "high_burnout",
        "eda_mean": 1.2,  "eda_std": 0.2,
        "hr_mean": 105,   "hr_std": 15,
        "acc_mean": 0.2,  "acc_std": 0.1,   # very low activity
        "sleep_dist": {"Wake": 0.55, "Light": 0.35, "Deep": 0.05, "REM": 0.05},
    },
]


def generate_profile(profile, n):
    eda = np.random.normal(profile["eda_mean"], profile["eda_std"], n).clip(0, None)
    hr  = np.random.normal(profile["hr_mean"],  profile["hr_std"],  n).clip(40, 180)
    acc = np.random.normal(profile["acc_mean"], profile["acc_std"], n).clip(0, None)

    # Sleep stages sampled from distribution
    stages = list(profile["sleep_dist"].keys())
    probs  = list(profile["sleep_dist"].values())
    sleep_stage = np.random.choice(stages, size=n, p=probs)

    df = pd.DataFrame({
        "EDA": eda,
        "HR": hr,
        "ACC": acc,
        "sleep_stage": sleep_stage,
        "profile": profile["name"],
    })
    return df


dfs = [generate_profile(p, SAMPLES_PER_PROFILE) for p in PROFILES]
merged = pd.concat(dfs, ignore_index=True)

merged.to_csv("merged_wearable_data.csv", index=False)
print(f"✅ Generated merged_wearable_data.csv  —  {len(merged):,} rows")
print(merged.head())
print("\nProfile distribution:")
print(merged["profile"].value_counts())
