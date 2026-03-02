import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from feature_engineering import extract_features
from utils import generate_burnout_label

# Load your merged dataset
df = pd.read_csv("merged_wearable_data.csv")

# Drop non-sensor columns if present (e.g. added by generate_data.py)
df = df.drop(columns=[col for col in ['profile'] if col in df.columns])

# Generate features row-wise (for time windows)
feature_list = []
labels = []

window_size = 500

for i in range(0, len(df) - window_size, window_size):
    window = df.iloc[i:i+window_size]
    features = extract_features(window)
    label = generate_burnout_label(features)

    feature_list.append(features)
    labels.append(label)

X = pd.concat(feature_list, ignore_index=True)
y = labels

# Sanity check: label distribution
import collections
print("Label distribution:", collections.Counter(y))

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Model
model = XGBClassifier(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    use_label_encoder=False,
    eval_metric='mlogloss',
    objective='multi:softprob',
    num_class=3
)

model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))

# Save model
joblib.dump(model, "model/burnout_model.pkl")

print("Model saved successfully.")