from flask import Blueprint, request, jsonify  # type: ignore
from core.gemini_client import ask_gemini  # type: ignore
from core.response_formatter import short_response

chat_bp = Blueprint("chat_bp", __name__)

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
        schema:
          type: object
          properties:
            response:
              type: string
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
    
    Question:
    {message}
    """
    
    raw_response = ask_gemini(system_prompt)
    response_text = short_response(raw_response)
    
    # Optional: Log Chat History to Supabase
    try:
        from core.supabase_client import supabase  # type: ignore
        supabase.table("advisory_chat_logs").insert({
            "user_message": message,
            "ai_response": response_text
        }).execute()
    except Exception as e:
        print(f"Warning: Failed to log chat to Supabase: {e}")
    
    return jsonify({
        "message": response_text
    })
