from flask import Blueprint, request, jsonify
from core.openai_service import ask_ai
import json

chat_bp = Blueprint('farmer_chat', __name__)

@chat_bp.route('/farmerChat', methods=['POST'])
def farmer_chat():
    data = request.json or {}
    question = data.get("question", "")
    
    prompt = f"""
    The farmer asks: "{question}"
    
    Answer the question as an expert agricultural assistant. Provide a direct, helpful, and concise response.
    Respond simply with plain text or markdown (no JSON required unless you want, but simple text is best for chat).
    """
    
    try:
        response_text = ask_ai(prompt)
        return jsonify({"answer": response_text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
