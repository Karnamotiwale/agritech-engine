import logging
from flask import Blueprint, request, jsonify
from core.supabase_client import supabase

logger = logging.getLogger(__name__)
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

        logger.info("[Valve] Logging OPEN action for farm_id=%s", irrigation.get('farm_id'))
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
            logger.info("[Valve] OPEN action logged to irrigation_logs and field_activities")
        except Exception as err:
            logger.warning("[Valve] Failed to log to new schema: %s", err)


        return jsonify({
            "command": "OPEN",
            "duration": data.get("duration", 10)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

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

        logger.info("[Valve] Logging STOP action for farm_id=%s", irrigation.get('farm_id'))
        supabase.table("irrigation_actions").insert(irrigation).execute()
        logger.info("[Valve] STOP action logged successfully.")

        return jsonify({"command": "STOP"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500
