from flask import Blueprint, request, jsonify
from core.gemini_service import ask_gemini
import json

sustainability_bp = Blueprint('sustainability', __name__)

@sustainability_bp.route('/sustainabilityAdvice', methods=['POST'])
def sustainability():
    """
    Get Sustainability Advice
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
    water_usage = data.get("water_usage", 0)
    fertilizer_usage = data.get("fertilizer_usage", 0)
    
    prompt = f"""
    Crop: {crop}
    Current Water Usage: {water_usage}
    Current Fertilizer Usage: {fertilizer_usage}
    
    Provide sustainability advice for this farm.
    Respond strictly in valid JSON without markdown tags.
    Format:
    {{
        "carbon_footprint_reduction": "strategies to reduce footprint",
        "sustainable_farming_practices": ["practice 1", "practice 2"]
    }}
    """
    
    try:
        response_text = ask_gemini(prompt)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
