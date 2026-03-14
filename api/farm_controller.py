from flask import Blueprint, jsonify
from core.supabase_client import supabase
from core.weather_engine import get_weather
from core.decision_engine import run_decision_engine

farm_api = Blueprint("farm_api", __name__)

@farm_api.route("/farm/dashboard/<farm_id>", methods=["GET"])
def get_farm_dashboard(farm_id):
    """
    Get Farm Dashboard Data
    ---
    tags:
      - Dashboard
    parameters:
      - name: farm_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Successful response
    """
    try:
        # Retrieve latest sensor data
        sensor_data_result = (
            supabase.table("sensor_readings")
            .select("*")
            .eq("device_id", farm_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        sensor = {}
        if sensor_data_result and sensor_data_result.data:
            s_data = sensor_data_result.data[0]
            sensor = {
                "moisture": s_data.get("moisture"),
                "nitrogen": s_data.get("nitrogen"),
                "phosphorus": s_data.get("phosphorus"),
                "potassium": s_data.get("potassium"),
                "temperature": s_data.get("temperature"),
                "humidity": s_data.get("humidity")
            }
        
        # Get Weather
        weather = get_weather(farm_id)

        # Re-run decision to display real-time result
        ai_decision = {}
        if sensor:
            decision = run_decision_engine(sensor)
            ai_decision = {
                "action": decision.get("action", "WAIT"),
                "confidence": decision.get("confidence", 0.8),
                "reason": decision.get("reason", "")
            }
            
        # Last Irrigation
        last_irrigation_result = (
            supabase.table("irrigation_actions")
            .select("*")
            .eq("farm_id", farm_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        
        last_irrigation = {}
        if last_irrigation_result and last_irrigation_result.data:
            last_irrigation = last_irrigation_result.data[0]

        return jsonify({
            "sensor": sensor,
            "weather": weather,
            "ai_decision": ai_decision,
            "last_irrigation": last_irrigation
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
