"""
Sustainability Advice Route
=============================
Uses centralized ask_gemini() with graceful fallback data.
"""
from flask import Blueprint, request, jsonify
from core.gemini_client import ask_gemini
import json

sustainability_bp = Blueprint('sustainability', __name__)


def _fallback_sustainability(crop, water_usage, fertilizer_usage):
    """Return sensible static advice when Gemini is unavailable."""
    return {
        "carbon_footprint_reduction": f"Reduce chemical fertilizer usage (currently {fertilizer_usage}) through precision application and switch to organic compost where possible.",
        "sustainable_farming_practices": [
            f"Optimize water usage (currently {water_usage}) with automated drip irrigation.",
            "Incorporate crop rotation to naturally replenish soil nutrients.",
            f"Use cover crops between {crop} seasons to prevent soil erosion.",
            "Adopt integrated pest management to reduce pesticide dependency."
        ]
    }


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

        # If Gemini returned a busy/failure message, use local fallback
        if "busy" in response_text.lower() or "offline" in response_text.lower() or "unavailable" in response_text.lower():
            return jsonify(_fallback_sustainability(crop, water_usage, fertilizer_usage)), 200

        try:
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            result = json.loads(clean_text)
        except Exception:
            result = _fallback_sustainability(crop, water_usage, fertilizer_usage)

        return jsonify(result), 200

    except Exception:
        # Never crash — return static advice
        return jsonify(_fallback_sustainability(crop, water_usage, fertilizer_usage)), 200
