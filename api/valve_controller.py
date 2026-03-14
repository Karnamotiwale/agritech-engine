from flask import Blueprint, request, jsonify
from core.supabase_client import supabase

valve_api = Blueprint("valve_api", __name__)

@valve_api.route("/valve/open", methods=["POST"])
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
        print("Valve OPEN action logged successfully.")

        return jsonify({
            "command": "OPEN",
            "duration": data.get("duration", 10)
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@valve_api.route("/valve/stop", methods=["POST"])
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
