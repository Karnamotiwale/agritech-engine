from flask import Blueprint, request, jsonify  # type: ignore
import requests
import os
from dotenv import load_dotenv

load_dotenv()

ai_advisory_bp = Blueprint("ai_advisory", __name__)

@ai_advisory_bp.route("/api/v1/ai-advisory", methods=["POST"])
def ai_advisory():
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

    Farmer Question:
    {question}
    """

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"reply": "AI service temporarily unavailable (API key missing)"}), 200

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    { "text": prompt }
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
        
        # Log raw response for debugging
        raw_data = response.text
        print("Raw Gemini Response:", raw_data)
        
        response.raise_for_status()
        
        # Parse response: response.candidates[0].content.parts[0].text
        data = response.json()
        ai_text = data["candidates"][0]["content"]["parts"][0]["text"]
        
        print("Parsed AI Text:", ai_text)
        
        return jsonify({
            "reply": ai_text
        }), 200
    except Exception as e:
        error_msg = str(e)
        print("Gemini API Error:", error_msg)
        return jsonify({
            "reply": f"Technical difficulty: {error_msg}"
        }), 200
