from flask import Blueprint, request, jsonify
from core.supabase_client import supabase

activity_bp = Blueprint("activity_bp", __name__)


@activity_bp.route("/api/v1/activities", methods=["GET", "POST"])
def activities_collection():
    """
    GET  — Get latest activities across all fields (when no field is selected)
    POST — Store a new field activity manually
    """
    if request.method == "GET":
        try:
            limit = request.args.get("limit", 20, type=int)
            response = (
                supabase.table("field_activities")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
                .execute()
            )
            return jsonify(response.data), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:  # POST
        try:
            data = request.json
            if not data:
                return jsonify({"error": "No data provided"}), 400
            response = supabase.table("field_activities").insert(data).execute()
            return jsonify(response.data[0] if response.data else {}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500



@activity_bp.route("/api/v1/activities/<field_id>", methods=["GET"])
def get_activities_by_field(field_id):
    """
    Get latest 10 activities for a specific field/farm
    Returns all if field_id == 'all'
    """
    try:
        query = supabase.table("field_activities").select("*")

        if field_id and field_id.lower() != "all":
            query = query.eq("field_id", field_id)

        response = query.order("created_at", desc=True).limit(10).execute()
        return jsonify(response.data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_bp.route("/api/v1/irrigation/log", methods=["POST"])
def log_irrigation():
    """
    Store irrigation execution — writes to irrigation_logs + field_activities
    """
    try:
        data = request.json or {}
        field_id = data.get("field_id") or None

        # 1. Store in irrigation_logs
        irrigation_data = {
            "field_id": field_id,
            "valve_id": data.get("valve_id", "Unknown"),
            "duration_minutes": int(data.get("duration_minutes", 0)),
            "water_volume": float(data.get("water_volume", 0.0)),
            "moisture_before": float(data.get("moisture_before", 0.0)),
            "moisture_after": float(data.get("moisture_after", 0.0)),
        }
        supabase.table("irrigation_logs").insert(irrigation_data).execute()

        # 2. Store in field_activities
        activity_data = {
            "field_id": field_id,
            "activity_type": "Irrigation",
            "growth_stage": data.get("growth_stage", "Vegetative"),
            "operation": data.get("operation", "Drip Irrigation"),
            "objective": data.get("objective", "Moisture Maintenance"),
            "method": data.get("method", "Drip"),
            "water_source": data.get("water_source", "Borewell"),
            "weather_condition": data.get("weather_condition", "Clear"),
            "notes": data.get("notes"),
            "crop_name": data.get("crop_name"),
            "farm_name": data.get("farm_name"),
        }
        supabase.table("field_activities").insert(activity_data).execute()

        return jsonify({"message": "Irrigation logged successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@activity_bp.route("/api/v1/fertilization/log", methods=["POST"])
def log_fertilization():
    """
    Store fertilization execution — writes to fertilization_logs + field_activities
    """
    try:
        data = request.json or {}
        field_id = data.get("field_id") or None

        # 1. Store in fertilization_logs
        fert_data = {
            "field_id": field_id,
            "fertilizer_type": data.get("fertilizer_type", "NPK"),
            "npk_ratio": data.get("npk_ratio", "14-14-14"),
            "quantity": float(data.get("quantity", 0.0)),
            "method": data.get("method", "Manual Spreading"),
        }
        supabase.table("fertilization_logs").insert(fert_data).execute()

        # 2. Store in field_activities
        activity_data = {
            "field_id": field_id,
            "activity_type": "Fertilization",
            "growth_stage": data.get("growth_stage", "Vegetative"),
            "operation": data.get("operation", "NPK Application"),
            "objective": data.get("objective", "Nutrient Boost"),
            "method": data.get("method", "Manual Spreading"),
            "water_source": data.get("water_source"),
            "weather_condition": data.get("weather_condition", "Clear"),
            "notes": data.get("notes"),
            "crop_name": data.get("crop_name"),
            "farm_name": data.get("farm_name"),
        }
        supabase.table("field_activities").insert(activity_data).execute()

        return jsonify({"message": "Fertilization logged successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
