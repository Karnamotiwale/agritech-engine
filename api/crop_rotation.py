from flask import Blueprint, request, jsonify
from core.openai_service import ask_ai
import json

rotation_bp = Blueprint('crop_rotation', __name__)

@rotation_bp.route('/cropRotation', methods=['POST'])
def crop_rotation():
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
        response_text = ask_ai(prompt)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
