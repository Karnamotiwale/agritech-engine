from flask import Blueprint, jsonify, request
from core.supabase_client import supabase
from core.weather_engine import get_weather
from core.decision_engine import run_decision_engine
from api.local_db_utils import get_all_farms, add_local_farm

farm_api = Blueprint("farm_api", __name__)

@farm_api.route("/api/v1/farms", methods=["GET"])
def get_farms():
    try:
        # Fetch farms from database (ignoring user_id for simplicity unless auth is setup)
        result = supabase.table("farms").select("*").execute()
        db_farms = result.data if result and result.data else []
        local_farms = get_all_farms()
        
        # Standardize units for output
        all_farms = db_farms + local_farms
        for f in all_farms:
            if "total_land_acres" in f:
                f["total_land_ha"] = round(f.pop("total_land_acres") * 0.404686, 2)
                
        return jsonify(all_farms), 200
    except Exception as e:
        return jsonify(get_all_farms()), 200

@farm_api.route("/api/v1/farms", methods=["POST"])
def create_farm():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        # Receive Hectares, store internally as acres until DB migration
        area_ha = float(data.get("area", 0))
        area_acres = area_ha / 0.404686
        
        farm_data = {
            "farm_name": data.get("name", "Unnamed Farm"),
            "total_land_acres": area_acres,
            "latitude": data.get("latitude", 0),
            "longitude": data.get("longitude", 0)
        }
        
        # Insert into Supabase
        try:
            result = supabase.table("farms").insert(farm_data).execute()
            if result and result.data:
                return jsonify(result.data[0]), 201
            else:
                return jsonify(add_local_farm(farm_data)), 201
        except Exception as e:
            # Fallback to local DB due to auth or FK error
            return jsonify(add_local_farm(farm_data)), 201
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@farm_api.route("/api/v1/farm/dashboard/<farm_id>", methods=["GET"])
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
