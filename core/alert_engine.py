"""
KisaanSaathi Smart Alert Engine
================================
Analyzes sensor readings to detect out-of-range water and fertilizer levels
and calls Gemini AI to generate a funny, emoji-rich farmer-friendly alert.
"""
import logging
from core.gemini_client import ask_gemini

# --------------------------------------------------
# THRESHOLDS (tunable)
# --------------------------------------------------
THRESHOLDS = {
    "soil_moisture": {"min": 35, "max": 75},   # % volumetric water content
    "nitrogen":      {"min": 50, "max": 200},  # mg/kg
    "phosphorus":    {"min": 20, "max": 100},  # mg/kg
    "potassium":     {"min": 40, "max": 180},  # mg/kg
}

FALLBACK_ALERTS = {
    "water_low":   "🚨🌵 Bhai, khet pyasa hai! Jaldi paani de! 💧",
    "water_high":  "🌊⚠️ Aye aye captain! Khet mein kashi ban rahi hai! Paani band karo! 🚫💦",
    "npk_low":     "😞🌱 Fasal ko bhooka mat raho! NPK ki zaroorat hai — khad dalo bhai! 🌾",
    "npk_high":    "🙈🔥 Zyada khilana bhi bura hota hai! Fertilizer overloaded — thoda control karo! 💊",
}


def _call_gemini_alert(issue_type: str, readings: dict) -> str:
    """
    Calls Gemini with specific soil context to generate a funny, friendly, emoji-rich alert.
    """
    moisture = readings.get("soil_moisture", "N/A")
    n = readings.get("nitrogen", "N/A")
    p = readings.get("phosphorus", "N/A")
    k = readings.get("potassium", "N/A")

    prompts = {
        "water_low": f"""
You are KisaanSaathi, a funny and caring AI farm assistant for Indian farmers. 
The soil moisture is {moisture}%, which is too LOW (should be 35-75%).
Write a SHORT alert message (max 2 lines) for the farmer in a mix of Hinglish/English.
Make it funny, empathetic and urgent with 2-3 relevant emojis.
DO NOT use hashtags. Just a natural, warm message telling them to IRRIGATE NOW.
""",
        "water_high": f"""
You are KisaanSaathi, a funny and caring AI farm assistant for Indian farmers.
The soil moisture is {moisture}%, which is too HIGH (should be 35-75%).
Write a SHORT alert message (max 2 lines) in a mix of Hinglish/English.
Make it funny and urgent with 2-3 relevant emojis.
Tell the farmer to STOP watering immediately before the roots drown.
""",
        "npk_low": f"""
You are KisaanSaathi, a funny and caring AI farm assistant for Indian farmers.
Nitrogen={n}, Phosphorus={p}, Potassium={k} — all LOW below recommended thresholds.
Write a SHORT alert (max 2 lines) in a mix of Hinglish/English.
Be funny, caring and urgent with 2-3 relevant emojis.
Tell them the crop is starving and needs fertilizer NOW.
""",
        "npk_high": f"""
You are KisaanSaathi, a funny and caring AI farm assistant for Indian farmers.
Nitrogen={n}, Phosphorus={p}, Potassium={k} — fertilizer levels are TOO HIGH.
Write a SHORT alert (max 2 lines) in a mix of Hinglish/English.
Make it funny but serious with 2-3 relevant emojis.
Tell them they are over-feeding the crop and to STOP applying fertilizer.
""",
    }

    prompt = prompts.get(issue_type)
    if not prompt:
        return FALLBACK_ALERTS.get(issue_type, "⚠️ Attention! Sensor levels are abnormal.")

    try:
        response = ask_gemini(prompt.strip())
        # Strip markdown formatting if Gemini includes it
        return response.replace("**", "").replace("*", "").strip()
    except Exception as e:
        logging.error(f"Gemini alert generation failed: {e}")
        return FALLBACK_ALERTS.get(issue_type, "⚠️ Attention! Sensor levels are abnormal.")


def analyze_and_generate_alerts(sensor: dict) -> list:
    """
    Given a sensor reading dict, checks all thresholds and returns a list of alert dicts.
    Each alert: { "type": str, "severity": "warning"|"critical", "message": str, "value": any }
    """
    alerts = []

    # ---- Water / Soil Moisture ----
    moisture = sensor.get("soil_moisture") or sensor.get("moisture")
    if moisture is not None:
        if moisture < THRESHOLDS["soil_moisture"]["min"]:
            severity = "critical" if moisture < 20 else "warning"
            msg = _call_gemini_alert("water_low", sensor)
            alerts.append({
                "type": "water_low",
                "title": "Low Water 💧",
                "severity": severity,
                "message": msg,
                "value": moisture,
                "unit": "%",
                "icon": "💧",
            })
        elif moisture > THRESHOLDS["soil_moisture"]["max"]:
            severity = "critical" if moisture > 90 else "warning"
            msg = _call_gemini_alert("water_high", sensor)
            alerts.append({
                "type": "water_high",
                "title": "Too Much Water 🌊",
                "severity": severity,
                "message": msg,
                "value": moisture,
                "unit": "%",
                "icon": "🌊",
            })

    # ---- Fertilizer / NPK ----
    nitrogen   = sensor.get("nitrogen")
    phosphorus = sensor.get("phosphorus")
    potassium  = sensor.get("potassium")

    npk_low = (
        (nitrogen   is not None and nitrogen   < THRESHOLDS["nitrogen"]["min"]) or
        (phosphorus is not None and phosphorus < THRESHOLDS["phosphorus"]["min"]) or
        (potassium  is not None and potassium  < THRESHOLDS["potassium"]["min"])
    )
    npk_high = (
        (nitrogen   is not None and nitrogen   > THRESHOLDS["nitrogen"]["max"]) or
        (phosphorus is not None and phosphorus > THRESHOLDS["phosphorus"]["max"]) or
        (potassium  is not None and potassium  > THRESHOLDS["potassium"]["max"])
    )

    if npk_low and not npk_high:
        msg = _call_gemini_alert("npk_low", sensor)
        alerts.append({
            "type": "npk_low",
            "title": "Low Nutrients 🌱",
            "severity": "warning",
            "message": msg,
            "value": {"N": nitrogen, "P": phosphorus, "K": potassium},
            "unit": "mg/kg",
            "icon": "🌱",
        })
    elif npk_high:
        msg = _call_gemini_alert("npk_high", sensor)
        alerts.append({
            "type": "npk_high",
            "title": "Over Fertilized 🔥",
            "severity": "warning",
            "message": msg,
            "value": {"N": nitrogen, "P": phosphorus, "K": potassium},
            "unit": "mg/kg",
            "icon": "🔥",
        })

    return alerts
