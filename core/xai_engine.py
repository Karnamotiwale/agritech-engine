def generate_explanation(data, ml_prediction, decision_result):
    factors = []

    if data["soil_moisture"] < 30:
        factors.append("Low soil moisture")

    if data["temperature"] > 32:
        factors.append("High temperature")

    if data["rain_forecast"] == 1:
        factors.append("Rain forecast present")

    confidence = 0.85 if ml_prediction == decision_result else 0.65

    explanation = {
        "decision": "Irrigate" if decision_result == 1 else "Do Not Irrigate",
        "factors": factors,
        "confidence": confidence,
        "summary": f"Decision taken based on {', '.join(factors)}"
    }

    return explanation
