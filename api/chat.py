"""
Farmer Advisory Chatbot
========================
Uses centralized ask_gemini() with keyword-based local fallback.
"""
from flask import Blueprint, request, jsonify
from core.gemini_client import ask_gemini
from core.response_formatter import short_response

chat_bp = Blueprint("chat_bp", __name__)

# ---------------------------------------------------------------------------
# LOCAL FALLBACK TIPS
# ---------------------------------------------------------------------------
CHAT_FALLBACKS = {
    "water": "💧 Water early morning or evening. Use drip irrigation to save water and improve root absorption.",
    "irrigation": "💧 Irrigate based on soil moisture — sandy soils need frequent watering, clay soils retain more moisture.",
    "yield": "🌾 Use balanced fertilizer, proper irrigation, healthy seeds, and timely pest control for best yields 🌱",
    "fertilizer": "🧪 Apply fertilizer based on soil test results. Too much can burn roots, too little starves your crops.",
    "soil": "🌍 Add organic compost to improve soil health. Test pH and nutrients every planting season.",
    "disease": "🔬 Remove infected leaves, apply neem oil, and rotate crops to prevent disease spread.",
    "pest": "🐛 Use neem spray, introduce beneficial insects, and keep fields clean of crop residue.",
    "weather": "🌦️ Check local forecasts daily. Protect crops from frost with mulch and ensure drainage for heavy rains.",
    "crop": "🌱 Choose varieties suited to your soil and climate. Practice rotation for long-term soil health.",
    "seed": "🌰 Use certified, disease-free seeds. Treat with fungicide before planting.",
    "harvest": "🌾 Harvest at the right maturity stage. Dry crops properly before storage to prevent mold.",
}

DEFAULT_FALLBACK = "🌱 Maintain proper irrigation, use balanced fertilizers, and monitor your crops regularly. Feel free to ask about water, soil, pests, or diseases!"


def _get_chat_fallback(message: str) -> str:
    """Match user message keywords to local farming tips."""
    msg = message.lower()
    for keyword, tip in CHAT_FALLBACKS.items():
        if keyword in msg:
            return tip
    return DEFAULT_FALLBACK


@chat_bp.route("/api/v1/chat", methods=["POST"])
def chat():
    """
    Farmer Advisory Chatbot
    ---
    tags:
      - Advisory AI

    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            message:
              type: string
              example: "How can I improve soil fertility?"

    responses:
      200:
        description: AI advisory response
    """
    data = request.json

    if not data or "message" not in data:
        return jsonify({"error": "Message is required"}), 400

    message = data["message"]

    system_prompt = f"""
    You are an expert agricultural advisor helping farmers.
    Answer in simple language suitable for farmers.

    Rules:
    • Give short answers only.
    • Maximum 2 sentences.
    • Do NOT return JSON.
    • Do NOT explain in detail.
    • Use simple farmer-friendly language.
    • Add 1-2 relevant emojis.

    Question:
    {message}
    """

    try:
        raw_response = ask_gemini(system_prompt)

        # Detect AI failure strings and substitute with local fallback
        if "busy" in raw_response.lower() or "offline" in raw_response.lower() or "unavailable" in raw_response.lower():
            response_text = _get_chat_fallback(message)
        else:
            response_text = short_response(raw_response)
    except Exception:
        response_text = _get_chat_fallback(message)

    # Best-effort chat logging (never blocks response)
    try:
        from core.supabase_client import supabase
        supabase.table("advisory_chat_logs").insert({
            "user_message": message,
            "ai_response": response_text
        }).execute()
    except Exception:
        pass

    return jsonify({"message": response_text})
