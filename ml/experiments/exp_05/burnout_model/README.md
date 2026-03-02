# Burnout & Overtraining Detection Model

This project implements a machine learning pipeline to detect burnout and overtraining risk based on wearable sensor data (Electrodermal Activity, Heart Rate, Accelerometer, and Sleep Stage).

## 🗂️ Project Structure

| File | Description |
|---|---|
| `feature_engineering.py` | Contains the logic for windowed feature extraction (HRV calculation, EDA peaks, sleep efficiency proxy). |
| `generate_data.py` | A utility to generate a synthetic dataset (`merged_wearable_data.csv`) for training/testing. |
| `train.py` | The main training script that processes the data and trains an XGBoost classifier. |
| `predict.py` | A batch inference script to run predictions on a full CSV of sensor data. |
| `single_inference.py` | A real-time assessor to get a risk profile from a single set of sensor parameters. |
| `utils.py` | Contains heuristic labeling logic and utility functions. |

---

## 🚀 How to Use

### 1. Prerequisites
Ensure you have Python installed, then install the required dependencies:
```bash
pip install xgboost scikit-learn pandas numpy joblib
```

### 2. Prepare Data
If you don't have a dataset yet, generate a synthetic one:
```bash
python generate_data.py
```
This creates `merged_wearable_data.csv` with 150,000 rows simulating different burnout profiles.

### 3. Train the Model
```bash
python train.py
```
This script will:
1. Extract features using a 500-sample window.
2. Label the data using diagnostic heuristics.
3. Train an **XGBoost Classifier**.
4. Save the model to `model/burnout_model.pkl`.

### 4. Run Inference (Predictions)

#### **Batch Mode (CSV)**
Analyze a full recording of sensor data:
```bash
python predict.py --input merged_wearable_data.csv
```

#### **Single Point Mode (Parameters)**
Instantly assess a specific state:
```bash
python single_inference.py --eda 1.2 --hr 105 --acc 0.1 --sleep Wake
```

---

## 🧠 Technical Overview

### Feature Engineering
The model transforms raw sensor signals into meaningful physiological indicators:
- **HRV (RMSSD)**: Measures autonomic nervous system variability from HR.
- **Resting HR**: Automatically identifies the 50 lowest HR samples in a window as the baseline.
- **Stress Peaks**: Counts EDA (sweat response) spikes above the window mean.
- **Sleep Efficiency**: Proxied via accelerometer stillness if sleep stage data is missing.

### Model Architecture
- **Classifier**: XGBoost (Extreme Gradient Boosting).
- **Classes**: 0 (Low Risk), 1 (Medium Risk), 2 (High Risk).
- **Evaluation**: Uses multiclass log-loss and stratified training to handle class distributions.

---

## ⚠️ Important Note on Labels
By default, this project uses **heuristic labels** (defined in `utils.py`) to generate "ground truth." In a clinical or production environment, these labels should be substituted for validated survey scores (e.g., Maslach Burnout Inventory) for true machine learning discovery.
