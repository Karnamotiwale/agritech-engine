from flask import Blueprint, request, jsonify
from core.gemini_service import ask_gemini
import json

disease_bp = Blueprint('disease_advice', __name__)

@disease_bp.route('/diseaseAdvice', methods=['POST'])
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
        response_text = ask_gemini(prompt)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
