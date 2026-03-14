from core.gemini_service import ask_gemini
import json

from core.policy_engine import is_action_allowed
from core.rl_engine import choose_action, get_state


def decide_action(ml_prediction, data):
    """
    Decide whether irrigation is required (1 = Yes, 0 = No)
    Uses OpenAI as the primary decision engine.

    data: dict with keys matching farm_data.csv columns
    """
    prompt = f"""
    Farm Data:
    Crop: {data.get("crop", "Unknown")}
    Soil Moisture (%): {data.get("soil_moisture_pct", 0)}
    Nitrogen (N): {data.get("nitrogen", data.get("nitrogen_kg_ha", 0))}
    Phosphorus (P): {data.get("phosphorus", data.get("phosphorus_kg_ha", 0))}
    Potassium (K): {data.get("potassium", data.get("potassium_kg_ha", 0))}
    Rain Forecast (mm): {data.get("rainfall", data.get("rainfall_mm", 0))}
    
    Analyze the conditions. Should the farmer irrigate? Should they fertigate? 
    Respond STRICTLY with valid JSON. Do not include markdown tags like ```json.
    Format:
    {{
        "irrigation_needed": 1 or 0,
        "fertigation_needed": 1 or 0,
        "reasoning": "Detailed explanation of why this action is needed",
        "confidence_explanation": "Explanation of your confidence in this decision based on the inputs"
    }}
    """
    
    try:
        response_text = ask_gemini(prompt)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)
        
        return {
            "decision": result.get("irrigation_needed", 0),
            "fertigation_needed": result.get("fertigation_needed", 0),
            "reason": result.get("reasoning", "AI decision"),
            "confidence": 0.9,
            "confidence_explanation": result.get("confidence_explanation", "")
        }
    except Exception as e:
        print(f"AI Decision Error: {e}")
        # Build RL state from data
        state = get_state(data)

        # RL suggested action (0 or 1)
        rl_action = choose_action(state)

        # ---------------- FALLBACK ----------------
        return {
            "decision": int(ml_prediction),
            "reason": "Fallback to ML prediction due to AI error."
        }


def run_decision_engine(sensor):
    from core.weather_engine import get_weather
    
    moisture = sensor.get("moisture", 0)
    farm_id = sensor.get("farm_id", "default")

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

