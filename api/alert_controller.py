"""
Smart Alert API Controller
===========================
Exposes:
  GET  /api/v1/alerts/latest        — Fetch latest alerts from DB (for polling)
  POST /api/v1/alerts/analyze       — Analyze given sensor payload and store alerts
  GET  /api/v1/alerts/live/<farm_id> — Analyze latest sensor_data for a farm and return alerts
"""
from flask import Blueprint, request, jsonify
from core.supabase_client import supabase
from core.alert_engine import analyze_and_generate_alerts
import logging, uuid
from datetime import datetime, timezone

alert_api = Blueprint("alert_api", __name__)


# ----------------------------------------------------------------
# GET /api/v1/alerts/latest  – returns last N alerts from DB
# ----------------------------------------------------------------
@alert_api.route("/api/v1/alerts/latest", methods=["GET"])
def get_latest_alerts():
    """
    Get Latest Smart Alerts
    ---
    tags:
      - Smart Alerts
    parameters:
      - name: limit
        in: query
        type: integer
        default: 10
    responses:
      200:
        description: List of latest smart alerts
    """
    try:
        limit = int(request.args.get("limit", 10))
        res = supabase.table("smart_alerts").select("*").order("created_at", desc=True).limit(limit).execute()
        return jsonify(res.data if res and res.data else []), 200
    except Exception as e:
        # If table doesn't exist yet, return empty silently
        return jsonify([]), 200


# ----------------------------------------------------------------
# GET /api/v1/alerts/live/<farm_id>
# Analyze newest sensor reading for a farm and return alerts
# ----------------------------------------------------------------
@alert_api.route("/api/v1/alerts/live/<farm_id>", methods=["GET"])
def live_alerts(farm_id):
    """
    Get Live AI Alerts for a Farm
    ---
    tags:
      - Smart Alerts
    parameters:
      - name: farm_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: List of current AI-generated alerts
    """
    try:
        res = (
            supabase.table("sensor_data")
            .select("*")
            .eq("farm_id", farm_id)
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )

        if not res or not res.data:
            return jsonify([]), 200

        sensor = res.data[0]
        alerts = analyze_and_generate_alerts(sensor)

        # Store alerts in Supabase (best-effort, ignore errors)
        _store_alerts(alerts, farm_id)

        return jsonify(alerts), 200
    except Exception as e:
        logging.error(f"Live alert error: {e}")
        return jsonify([]), 200


# ----------------------------------------------------------------
# POST /api/v1/alerts/analyze  – manual push from sensor/worker
# ----------------------------------------------------------------
@alert_api.route("/api/v1/alerts/analyze", methods=["POST"])
def analyze_sensor():
    """
    Analyze Sensor Payload and Generate AI Alerts
    ---
    tags:
      - Smart Alerts
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Generated alerts
    """
    try:
        sensor = request.json
        if not sensor:
            return jsonify({"error": "No sensor data provided"}), 400

        farm_id = sensor.get("farm_id", "default")
        alerts  = analyze_and_generate_alerts(sensor)
        _store_alerts(alerts, farm_id)

        return jsonify({"alerts": alerts, "count": len(alerts)}), 200
    except Exception as e:
        logging.error(f"Analyze alert error: {e}")
        return jsonify({"error": "An internal error occurred"}), 500


# ----------------------------------------------------------------
# Helper: persist alerts to Supabase (best-effort)
# ----------------------------------------------------------------
def _store_alerts(alerts: list, farm_id: str):
    if not alerts:
        return
    try:
        rows = [
            {
                "id": str(uuid.uuid4()),
                "farm_id": farm_id,
                "alert_type": a["type"],
                "title": a["title"],
                "severity": a["severity"],
                "message": a["message"],
                "icon": a.get("icon", "⚠️"),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            for a in alerts
        ]
        supabase.table("smart_alerts").insert(rows).execute()
    except Exception as e:
        logging.warning(f"Could not store alerts in DB: {e}")
