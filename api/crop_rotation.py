from flask import Blueprint, request, jsonify  # type: ignore

rotation_bp = Blueprint('crop_rotation', __name__)

@rotation_bp.route('/api/v1/crops/rotation', methods=['POST'])
def crop_rotation():
    """
    Suggest Next Crop for Rotation
    """
    data = request.json or {}
    previous_crops = data.get("previous_crops", [])
    
    try:
        last_crop = previous_crops[-1].lower() if previous_crops else "unknown"
        if last_crop in ["wheat", "corn", "maize"]:
            short_message = "Plant legumes next. They will fix nitrogen in the soil depleted by cereal crops."
        elif last_crop in ["legumes", "soybeans", "peas", "pulses"]:
            short_message = "Plant wheat next. Cereal crops benefit from the nitrogen fixed by previous legume crops."
        else:
            short_message = "Plant a general cover crop next to restore soil health and prevent erosion."
            
        return jsonify({"message": short_message}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
