from flask import Blueprint, request, jsonify

import json

rotation_bp = Blueprint('crop_rotation', __name__)

@rotation_bp.route('/cropRotation', methods=['POST'])
def crop_rotation():
    """
    Suggest Next Crop for Rotation
    ---
    tags:
      - Agronomy
    parameters:
      - in: body
        name: body
        schema:
          type: object
    responses:
      200:
        description: Successful response
    """
    data = request.json or {}
    previous_crops = data.get("previous_crops", [])
    
    prompt = f"""
    History of crops grown on this field: {previous_crops}
    
    Based on this history, suggest the best next crop to plant to improve soil health.
    Respond strictly in valid JSON without markdown tags.
    Format:
    {{
        "next_crop": "suggested crop name",
        "soil_health_benefits_explanation": "detailed reasoning"
    }}
    """
    
    try:
        last_crop = previous_crops[-1].lower() if previous_crops else "unknown"
        if last_crop in ["wheat", "corn", "maize"]:
            next_crop = "legumes"
            reason = "Legumes fix nitrogen in the soil, which is depleted by cereal crops."
        elif last_crop in ["legumes", "soybeans", "peas", "pulses"]:
            next_crop = "wheat"
            reason = "Cereal crops benefit from the nitrogen fixed by previous legume crops."
        else:
            next_crop = "cover crop"
            reason = "A general cover crop helps restore soil health and prevent erosion."
            
        result = {
            "next_crop": next_crop,
            "soil_health_benefits_explanation": reason
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
