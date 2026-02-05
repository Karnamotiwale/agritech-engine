import pandas as pd
import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score
import os

# Ensure models directory exists
if not os.path.exists("models"):
    os.makedirs("models")

# Load dataset
try:
    data = pd.read_csv("data/farm_data.csv")
except FileNotFoundError:
    print("Error: data/farm_data.csv not found.")
    # Create dummy data for testing if file missing (dev mode fallback)
    print("Creating dummy data for training...")
    data = pd.DataFrame({
        "soil_moisture": [40, 20, 60, 10, 30] * 20,
        "temperature": [25, 30, 20, 35, 28] * 20,
        "humidity": [60, 40, 70, 30, 50] * 20,
        "rain_forecast": [10, 0, 20, 0, 50] * 20,
        "irrigate": [0, 1, 0, 1, 0] * 20
    })

# Features and target
X = data[["soil_moisture", "temperature", "humidity", "rain_forecast"]]
y = data["irrigate"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train XGBoost model
model = XGBClassifier(
    n_estimators=200,
    max_depth=6,
    learning_rate=0.1,
    random_state=42,
    eval_metric='logloss'
)

model.fit(X_train, y_train)

# Predictions
preds = model.predict(X_test)

# Metrics
accuracy = accuracy_score(y_test, preds)
precision = precision_score(y_test, preds, zero_division=0)

print(f"Accuracy: {accuracy}")
print(f"Precision: {precision}")

# Save model
joblib.dump(model, "models/xgb_model.pkl")

# Save metrics
metrics = {
    "accuracy": float(accuracy),
    "precision": float(precision)
}
joblib.dump(metrics, "models/model_metrics.pkl")
print("Model and metrics saved.")
