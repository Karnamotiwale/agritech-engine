from flask import Blueprint, request, jsonify
from core.supabase_client import supabase

valve_api = Blueprint("valve_api", __name__)

@valve_api.route("/api/v1/valves/open", methods=["POST"])
def open_valve():
    """
    Open Irrigation Valve
    ---
    tags:
      - Valve Control
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Successful response returning command payload
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        irrigation = {
            "farm_id": data.get("farm_id"),
            "crop_id": data.get("crop_id"),
            "action": "IRRIGATE",
            "duration": data.get("duration", 10)
        }

        print(f"Logging valve OPEN action: {irrigation}")
        supabase.table("irrigation_actions").insert(irrigation).execute()
        
        try:
            field_id_val = str(data.get("farm_id", ""))
            
            # Store in irrigation_logs
            irrigation_data = {
                "field_id": field_id_val if field_id_val else None,
                "valve_id": str(data.get("valve_id", "Unknown")),
                "duration_minutes": int(data.get("duration", 10)),
                "water_volume": 0.0,
                "moisture_before": 0.0,
                "moisture_after": 0.0
            }
            supabase.table("irrigation_logs").insert(irrigation_data).execute()
            
            # Store in field_activities
            activity_data = {
                "field_id": field_id_val if field_id_val else None,
                "activity_type": "Irrigation",
                "growth_stage": "Unknown",
                "operation": "Valve Opened",
                "objective": "Irrigation Execution",
                "method": "Automated",
                "water_source": "Unknown",
                "weather_condition": "Unknown"
            }
            supabase.table("field_activities").insert(activity_data).execute()
            print("Valve OPEN action logged successfully in new tables.")
        except Exception as err:
            print(f"Failed to log to new schema: {err}")


        return jsonify({
            "command": "OPEN",
            "duration": data.get("duration", 10)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@valve_api.route("/api/v1/valves/stop", methods=["POST"])
def close_valve():
    """
    Stop Irrigation Valve
    ---
    tags:
      - Valve Control
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Successful response
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        irrigation = {
            "farm_id": data.get("farm_id"),
            "crop_id": data.get("crop_id"),
            "action": "STOP"
        }

        print(f"Logging valve STOP action: {irrigation}")
        supabase.table("irrigation_actions").insert(irrigation).execute()
        print("Valve STOP action logged successfully.")

        return jsonify({"command": "STOP"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
