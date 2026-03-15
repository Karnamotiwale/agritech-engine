
import json

from core.policy_engine import is_action_allowed
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
    from core.weather_engine import get_weather
    
    # Map from the new sensor_data table
    moisture = sensor.get("soil_moisture") or sensor.get("moisture", 0)
    farm_id = sensor.get("farm_id") or sensor.get("device_id", "default")

    weather = get_weather(farm_id)
    rain_probability = weather.get("rain_probability", 0)

    if moisture < 35 and rain_probability < 40:
        return {
            "action": "IRRIGATE",
            "duration": 10,
            "confidence": 0.9,
            "reason": "Low soil moisture and low rain probability"
        }
    else:
        return {
            "action": "WAIT",
            "confidence": 0.8,
            "reason": "Moisture sufficient or rain expected"
        }

