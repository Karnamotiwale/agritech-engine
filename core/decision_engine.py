import logging

from core.rl_engine import choose_action, get_state


def decide_action(ml_prediction, data):
    """
    Decide whether irrigation is required (1 = Yes, 0 = No)
    Uses ML and RL as the primary decision engine.

    data: dict with keys matching farm_data.csv columns
    """
    
    # Build RL state from data
    state = get_state(data)

    # RL suggested action (0 or 1)
    rl_action = choose_action(state)

    # Use ML prediction as the primary decision to keep it rule-based and ML-driven
    return {
        "decision": int(ml_prediction),
        "reason": "Decision based on XGBoost ML prediction and local parameters."
    }


def run_decision_engine(sensor):
    """
    Full AI loop decision:
      1. Fetch weather context
      2. Try ML model (RandomForest) as primary signal
      3. Fall back to moisture + rain threshold rules if ML unavailable
    """
    from core.weather_engine import get_weather

    # Map from the new sensor_data table schema
    moisture = float(sensor.get("soil_moisture") or sensor.get("moisture") or 0)
    farm_id = sensor.get("farm_id") or sensor.get("device_id", "default")

    weather = get_weather(farm_id)
    rain_probability = weather.get("rain_probability", 0)
    temperature = weather.get("temperature", 30)
    humidity = weather.get("humidity", 65)

    # --- Try ML model first ---
    try:
        import pickle, os
        model_path = "models/model.pkl"
        if os.path.exists(model_path):
            with open(model_path, "rb") as f:
                saved = pickle.load(f)
            model = saved["model"]

            crop_enc = saved["crop_encoder"]
            stage_enc = saved["stage_encoder"]
            risk_enc = saved["risk_encoder"]

            crop_val = "wheat"
            stage_val = "Vegetative"
            risk_val = "low"

            # Safe-encode: if unknown label, fall back to index 0
            try:
                crop_idx = crop_enc.transform([crop_val])[0]
            except Exception:
                crop_idx = 0
            try:
                stage_idx = stage_enc.transform([stage_val])[0]
            except Exception:
                stage_idx = 0
            try:
                risk_idx = risk_enc.transform([risk_val])[0]
            except Exception:
                risk_idx = 0

            X = [[
                crop_idx,
                moisture,
                temperature,
                humidity,
                rain_probability,
                7.0,    # soil_ph default
                sensor.get("nitrogen", 50),
                sensor.get("phosphorus", 30),
                sensor.get("potassium", 40),
                stage_idx,
                risk_idx,
                risk_idx,
            ]]
            ml_prediction = int(model.predict(X)[0])

            if ml_prediction == 1:
                return {
                    "action": "IRRIGATE",
                    "duration": 10,
                    "confidence": 0.85,
                    "source": "ml_model",
                    "reason": f"ML model predicts irrigation needed. Moisture={moisture}%, Rain prob={rain_probability}%"
                }
            else:
                return {
                    "action": "WAIT",
                    "confidence": 0.80,
                    "source": "ml_model",
                    "reason": f"ML model predicts no irrigation needed. Moisture={moisture}%"
                }
    except Exception as ml_err:
        logging.warning(f"ML model unavailable, falling back to rule engine: {ml_err}")

    # --- Rule-based fallback ---
    if moisture < 35 and rain_probability < 40:
        return {
            "action": "IRRIGATE",
            "duration": 10,
            "confidence": 0.9,
            "source": "rule_engine",
            "reason": "Low soil moisture and low rain probability"
        }
    else:
        return {
            "action": "WAIT",
            "confidence": 0.8,
            "source": "rule_engine",
            "reason": "Moisture sufficient or rain expected"
        }
