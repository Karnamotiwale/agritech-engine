from flask import Blueprint, request, jsonify
from core.supabase_client import supabase
from core.decision_engine import run_decision_engine

sensor_api = Blueprint("sensor_api", __name__)

@sensor_api.route("/api/v1/sensors/data", methods=["POST"])
def receive_sensor_data():
    """
    Receive Sensor Data
    ---
    tags:
      - Sensors
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Successful response containing AI decision
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        sensor_payload = {
            "device_id": data.get("farm_id"), 
            "moisture": data.get("moisture")
        }

        # Store data in Supabase sensor_readings table
        print(f"Inserting sensor reading: {sensor_payload}")
        supabase.table("sensor_readings").insert(sensor_payload).execute()
        print("Sensor reading inserted successfully.")

        # Call AI decision engine
        print(f"Triggering run_decision_engine for payload: {sensor_payload}")
        decision = run_decision_engine(sensor_payload)
        print(f"Decision engine returned: {decision}")

        return jsonify({
            "status": "ok",
            "decision": decision
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@sensor_api.route("/api/v1/sensors/live/<farm_id>", methods=["GET"])
def get_live_sensor(farm_id):
    """
    Get live sensor readings for a farm
    ---
    tags:
      - Sensors
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
        data = (
            supabase.table("sensor_readings")
            .select("*")
            .eq("device_id", farm_id) # farm_id is mapped to device_id
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return jsonify(data.data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
