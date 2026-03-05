def generate_burnout_label(features):
    score = 0

    if features['mean_eda'].values[0] > 0.5:
        score += 1

    if features['sleep_efficiency'].values[0] < 0.8:
        score += 1

    if features['hrv_rmssd'].values[0] < 0.03:
        score += 1

    if features['mean_hr'].values[0] > 90:
        score += 1

    if score >= 3:
        return 2  # High Risk
    elif score == 2:
        return 1  # Medium Risk
    else:
        return 0  # Low Risk