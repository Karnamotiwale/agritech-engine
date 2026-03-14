from flask import Blueprint, request, jsonify

import json

disease_bp = Blueprint('disease_advice', __name__)

@disease_bp.route('/api/v1/ai/disease-advice', methods=['POST'])
def disease_advice():
    """
    Get Disease Treatment Advice
    ---
    tags:
      - Advisories
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
    crop = data.get("crop", "Unknown")
    disease_name = data.get("disease_name", "Unknown")
    
    prompt = f"""
    Crop: {crop}
    Disease: {disease_name}
    
    Provide treatment advice for this disease on this crop.
    Respond strictly in valid JSON without markdown tags.
    Format:
    {{
        "recommended_pesticide": "string",
        "dosage_instructions": "string",
        "prevention_advice": "string"
    }}
    """
    
    try:
        result = {
            "recommended_pesticide": f"Standard treatment for {disease_name}",
            "dosage_instructions": "Follow manufacturer's guidelines on the label.",
            "prevention_advice": f"Ensure proper spacing and prune infected leaves to prevent {disease_name}."
        }
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
