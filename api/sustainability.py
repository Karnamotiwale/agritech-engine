from flask import Blueprint, request, jsonify
from core.gemini_client import ask_gemini
import json

sustainability_bp = Blueprint('sustainability', __name__)

@sustainability_bp.route('/api/v1/ai/sustainability-advice', methods=['POST'])
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
        
        try:
            # Clean possible markdown block before parsing
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_text)
        except:
            # Fallback if Gemini failed to output valid JSON
            result = {
                "carbon_footprint_reduction": f"Consider reducing chemical fertilizer ({fertilizer_usage}) through precision application. {response_text[:50]}",
                "sustainable_farming_practices": [
                    f"Optimize water usage (currently at {water_usage}) using automated drip irrigation.",
                    "Incorporate crop rotation to naturally replenish soil nutrients."
                ]
            }
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
