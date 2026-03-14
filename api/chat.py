from flask import Blueprint, request, jsonify
from core.gemini_client import ask_gemini

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
    
    Question:
    {message}
    
    Provide:
    • practical advice
    • crop recommendations
    • fertilizer suggestions if relevant
    • prevention tips if disease related
    """
    
    response_text = ask_gemini(system_prompt)
    
    # Optional: Log Chat History to Supabase
    try:
        from core.supabase_client import supabase
        supabase.table("advisory_chat_logs").insert({
            "user_message": message,
            "ai_response": response_text
        }).execute()
    except Exception as e:
        print(f"Warning: Failed to log chat to Supabase: {e}")
    
    return jsonify({
        "response": response_text
    })
