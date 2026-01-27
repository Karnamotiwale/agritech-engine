import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Load dataset
data = pd.read_csv("data/farm_data.csv")

X = data.drop("irrigate", axis=1)
y = data["irrigate"]

# Train model
model = RandomForestClassifier(n_estimators=50, random_state=42)
model.fit(X, y)

# Save model
os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ AI Engine: Model trained and saved")
