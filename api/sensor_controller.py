from flask import Blueprint, request, jsonify
from core.supabase_client import supabase
from core.decision_engine import run_decision_engine

sensor_api = Blueprint("sensor_api", __name__)


# ─────────────────────────────────────────────────────────────
# EXISTING ENDPOINT: Receive moisture-only sensor data (legacy)
# ─────────────────────────────────────────────────────────────
@sensor_api.route("/api/v1/sensors/data", methods=["POST"])
def receive_sensor_data():
    """
    Receive Sensor Data (legacy moisture-only)
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

        raw_moisture = data.get("moisture")
        if raw_moisture is not None and isinstance(raw_moisture, (int, float)) and raw_moisture > 100:
            raw_moisture = float("{:.2f}".format((raw_moisture / 1023.0) * 100.0))

        sensor_payload = {
            "device_id": data.get("farm_id"),
            "moisture": raw_moisture
        }

        supabase.table("sensor_readings").insert(sensor_payload).execute()

        decision = run_decision_engine(sensor_payload)

        return jsonify({"status": "ok", "decision": decision}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@sensor_api.route("/api/v1/sensors/live/<farm_id>", methods=["GET"])
def get_live_sensor(farm_id):
    """
    Get live sensor readings for a farm (legacy moisture-only)
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
            .eq("device_id", farm_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        return jsonify(data.data), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────
# NEW ENDPOINT: Ingest full NPK + Moisture sensor payload
# Called by ESP8266 in the field
# ─────────────────────────────────────────────────────────────
@sensor_api.route("/api/v1/sensors", methods=["POST"])
def add_sensor_data():
    """
    Ingest full sensor data (soil moisture + NPK + temperature + humidity)
    ---
    tags:
      - Sensors
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            farm_id:
              type: string
            soil_moisture:
              type: number
            nitrogen:
              type: number
            phosphorus:
              type: number
            potassium:
              type: number
            temperature:
              type: number
            humidity:
              type: number
    responses:
      200:
        description: Sensor data saved successfully
    """
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400

        payload = {
            "farm_id":       data.get("farm_id"),
            "soil_moisture": data.get("soil_moisture"),
            "nitrogen":      data.get("nitrogen"),
            "phosphorus":    data.get("phosphorus"),
            "potassium":     data.get("potassium"),
            "temperature":   data.get("temperature"),
            "humidity":      data.get("humidity"),
        }

        # Remove None values so Supabase uses column defaults
        payload = {k: v for k, v in payload.items() if v is not None}

        supabase.table("sensor_data").insert(payload).execute()

        return jsonify({"status": "saved", "data": payload}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────
# NEW ENDPOINT: Get latest NPK + Moisture reading
# Polled by React dashboard every 5 seconds
# ─────────────────────────────────────────────────────────────
@sensor_api.route("/api/v1/sensors/latest", methods=["GET"])
def get_latest_sensor():
    """
    Get the latest full NPK + moisture sensor reading
    ---
    tags:
      - Sensors
    parameters:
      - name: farm_id
        in: query
        type: string
        required: false
    responses:
      200:
        description: Latest sensor data row
    """
    try:
        farm_id = request.args.get("farm_id")

        query = supabase.table("sensor_data").select("*").order("created_at", desc=True).limit(1)

        if farm_id:
            query = query.eq("farm_id", farm_id)

        result = query.execute()

        if result.data:
            return jsonify(result.data[0]), 200
        else:
            return jsonify({"status": "no_data", "message": "No sensor readings found yet"}), 404

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────
# NEW ENDPOINT: Get sensor history (last N readings)
# ─────────────────────────────────────────────────────────────
@sensor_api.route("/api/v1/sensors/history", methods=["GET"])
def get_sensor_history():
    """
    Get recent sensor data history
    ---
    tags:
      - Sensors
    parameters:
      - name: farm_id
        in: query
        type: string
        required: false
      - name: limit
        in: query
        type: integer
        required: false
    responses:
      200:
        description: Array of sensor readings
    """
    try:
        farm_id = request.args.get("farm_id")
        limit   = int(request.args.get("limit", 20))

        query = supabase.table("sensor_data").select("*").order("created_at", desc=True).limit(limit)

        if farm_id:
            query = query.eq("farm_id", farm_id)

        result = query.execute()
        return jsonify(result.data), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
