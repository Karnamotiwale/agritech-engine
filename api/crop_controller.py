from flask import Blueprint, jsonify, request
from core.supabase_client import supabase

crop_api = Blueprint("crop_api", __name__)

@crop_api.route("/api/v1/crops", methods=["GET"])
def get_crops():
    try:
        from api.local_db_utils import get_all_crops
        farm_id = request.args.get("farm_id")
        query = supabase.table("crops").select("*")
        if farm_id:
            query = query.eq("farm_id", farm_id)
            
        result = query.execute()
        db_crops = result.data if result and result.data else []
        local_crops = get_all_crops(farm_id)
        return jsonify(db_crops + local_crops), 200
    except Exception as e:
        from api.local_db_utils import get_all_crops
        return jsonify(get_all_crops(request.args.get("farm_id"))), 200

@crop_api.route("/api/v1/crops", methods=["POST"])
def create_crop():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        crop_data = {
            "farm_id": data.get("farmId"),
            "crop_name": data.get("name"),
            "crop_type": data.get("cropType"),
            "sowing_date": data.get("sowingDate"),
            "seeds_planted": data.get("seedsPlanted", 0),
            "image_url": data.get("image")
        }
        
        # Clean null values
        crop_data = {k: v for k, v in crop_data.items() if v is not None}
        
        try:
            result = supabase.table("crops").insert(crop_data).execute()
            if result and result.data:
                return jsonify(result.data[0]), 201
            else:
                from api.local_db_utils import add_local_crop
                return jsonify(add_local_crop(crop_data)), 201
        except Exception as e:
            # Fallback to local db if Supabase blocks constraints
            from api.local_db_utils import add_local_crop
            return jsonify(add_local_crop(crop_data)), 201
            
    except Exception as e:
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500
