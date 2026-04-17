"""
AI Advisory Route
==================
Uses the centralized ask_gemini() client — never calls Gemini REST API directly.
Includes keyword-based fallback tips when AI is unavailable.
"""
from flask import Blueprint, request, jsonify

ai_advisory_bp = Blueprint("ai_advisory", __name__)

# ---------------------------------------------------------------------------
# LOCAL FARMING FALLBACK TIPS (used when Gemini is down)
# ---------------------------------------------------------------------------
FARMING_TIPS = {
    "water": "💧 Water your crops early morning or late evening to reduce evaporation. Use drip irrigation for best results.",
    "irrigation": "💧 Schedule irrigation based on soil moisture levels. Sandy soils need more frequent watering than clay soils.",
    "yield": "🌾 Use balanced NPK fertilizer, ensure proper spacing, use certified seeds, and maintain timely pest control for best yields.",
    "fertilizer": "🧪 Apply nitrogen during vegetative stage, phosphorus at planting, and potassium during fruiting. Avoid over-application.",
    "soil": "🌍 Test soil pH and nutrients every season. Add organic compost to improve structure and water retention.",
    "disease": "🔬 Remove infected leaves immediately. Use neem oil spray as organic treatment. Rotate crops each season to break disease cycles.",
    "pest": "🐛 Use integrated pest management: introduce beneficial insects, apply neem-based sprays, and remove crop residue after harvest.",
    "weather": "🌦️ Monitor local forecasts daily. Protect crops from frost with mulching. Ensure drainage during heavy rains.",
    "crop": "🌱 Choose crop varieties suited to your local climate and soil type. Practice crop rotation for soil health.",
    "seed": "🌰 Always use certified, disease-free seeds. Treat seeds with fungicide before planting for better germination.",
}

DEFAULT_TIP = "🌱 For best results, maintain proper irrigation, use balanced fertilizers, and monitor your crops regularly. Ask me a specific question about water, soil, pests, or diseases!"


def _get_fallback_tip(question: str) -> str:
    """Match user question keywords to local farming tips."""
    q = question.lower()
    for keyword, tip in FARMING_TIPS.items():
        if keyword in q:
            return tip
    return DEFAULT_TIP


@ai_advisory_bp.route("/api/v1/ai-advisory", methods=["POST"])
def ai_advisory():
    """
    AI Advisory Endpoint
    ---
    tags:
      - Advisory AI
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
    responses:
      200:
        description: AI advisory reply
    """
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    question = data.get("message")
    if not question:
        return jsonify({"error": "No message provided"}), 400

    prompt = f"""
    You are an agricultural expert advisor.
    Answer the farmer question clearly and practically. Focus on actionable insights.

    Rules:
    • Give short answers only.
    • Maximum 2 sentences.
    • Do NOT return JSON.
    • Do NOT explain in detail.
    • Use simple farmer-friendly language.
    • Add 1-2 relevant emojis.

    Farmer Question:
    {question}
    """

    try:
        from core.gemini_client import ask_gemini
        response = ask_gemini(prompt)

        # Detect AI failure strings and substitute with local fallback
        if "busy" in response.lower() or "offline" in response.lower() or "unavailable" in response.lower():
            response = _get_fallback_tip(question)

        return jsonify({"reply": response}), 200

    except Exception as e:
        # Never leak technical errors — return farming tip instead
        return jsonify({"reply": _get_fallback_tip(question)}), 200
