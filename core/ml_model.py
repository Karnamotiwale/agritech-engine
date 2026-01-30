import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split


MODEL_PATH = "models/model.pkl"
DATA_PATH = "data/farm_data.csv"


class IrrigationMLModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )

        # Encoders for categorical columns
        self.crop_encoder = LabelEncoder()
        self.stage_encoder = LabelEncoder()
        self.risk_encoder = LabelEncoder()

    def load_and_prepare_data(self):
        df = pd.read_csv(DATA_PATH)

        # Encode categorical columns
        df["crop"] = self.crop_encoder.fit_transform(df["crop"])
        df["growth_stage"] = self.stage_encoder.fit_transform(df["growth_stage"])
        df["disease_risk"] = self.risk_encoder.fit_transform(df["disease_risk"])
        df["pest_risk"] = self.risk_encoder.fit_transform(df["pest_risk"])

        X = df[
            [
                "crop",
                "soil_moisture_pct",
                "temperature_c",
                "humidity_pct",
                "rainfall_mm",
                "soil_ph",
                "nitrogen_kg_ha",
                "phosphorus_kg_ha",
                "potassium_kg_ha",
                "growth_stage",
                "disease_risk",
                "pest_risk"
            ]
        ]

        y = df["irrigation_required"]

        return train_test_split(X, y, test_size=0.2, random_state=42)

    def train(self):
        X_train, X_test, y_train, y_test = self.load_and_prepare_data()
        self.model.fit(X_train, y_train)

        with open(MODEL_PATH, "wb") as f:
            pickle.dump(
                {
                    "model": self.model,
                    "crop_encoder": self.crop_encoder,
                    "stage_encoder": self.stage_encoder,
                    "risk_encoder": self.risk_encoder
                },
                f
            )

    def predict(self, data: dict):
        with open(MODEL_PATH, "rb") as f:
            saved = pickle.load(f)

        model = saved["model"]

        # Encode incoming categorical values
        crop = saved["crop_encoder"].transform([data["crop"]])[0]
        stage = saved["stage_encoder"].transform([data["growth_stage"]])[0]
        disease_risk = saved["risk_encoder"].transform([data["disease_risk"]])[0]
        pest_risk = saved["risk_encoder"].transform([data["pest_risk"]])[0]

        X = [[
            crop,
            data["soil_moisture_pct"],
            data["temperature_c"],
            data["humidity_pct"],
            data["rainfall_mm"],
            data["soil_ph"],
            data["nitrogen_kg_ha"],
            data["phosphorus_kg_ha"],
            data["potassium_kg_ha"],
            stage,
            disease_risk,
            pest_risk
        ]]

        prediction = model.predict(X)[0]
        return int(prediction)
if __name__ == "__main__":
    model = IrrigationMLModel()
    model.train()
    print("✅ Model retrained and saved successfully")
