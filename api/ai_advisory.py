from flask import Blueprint, request, jsonify  # type: ignore
from core.gemini_client import ask_gemini  # type: ignore
from core.response_formatter import short_response

ai_advisory_bp = Blueprint("ai_advisory", __name__)

@ai_advisory_bp.route("/api/v1/ai-advisory", methods=["POST"])
def ai_advisory():
    data = request.json
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
        
    question = data.get("question")
    if not question:
        return jsonify({"error": "No question provided"}), 400

    prompt = f"""
    You are an agricultural expert advisor.
    Answer the farmer question clearly and practically. Focus on actionable insights.

    Rules:
    • Give short answers only.
    • Maximum 2 sentences.
    • Do NOT return JSON.
    • Do NOT explain in detail.
    • Use simple farmer-friendly language.

    Farmer Question:
    {question}
    """

    raw_response = ask_gemini(prompt)
    response_text = short_response(raw_response)

    return jsonify({
        "message": response_text
    }), 200
