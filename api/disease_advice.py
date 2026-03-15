from flask import Blueprint, request, jsonify  # type: ignore

disease_bp = Blueprint('disease_advice', __name__)

@disease_bp.route('/api/v1/ai/disease-advice', methods=['POST'])
def disease_advice():
    """
    Get Disease Treatment Advice
    """
    data = request.json or {}
    crop = data.get("crop", "Unknown")
    disease_name = data.get("disease_name", "Unknown")
    
    try:
        short_message = f"{disease_name} detected on {crop}. Apply standard treatment and prune infected leaves."
        return jsonify({"message": short_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

