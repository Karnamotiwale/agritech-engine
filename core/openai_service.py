import os
import json
from openai import OpenAI

# Initialize the OpenAI client securely
# Try VITE_OPENAI_API_KEY first as it exists in the user's .env file
api_key = os.getenv("VITE_OPENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    print(f"Failed to initialize OpenAI client: {e}")
    client = None

def ask_ai(prompt: str, system_instruction: str = None) -> str:
    """
    Centralized function to communicate with OpenAI.
    """
    if not client:
        return json.dumps({"error": "OpenAI client is not initialized Check API KEY"})

    if not system_instruction:
        system_instruction = "You are an agriculture expert AI that helps farmers with irrigation decisions, fertilization, crop health monitoring, yield prediction, and sustainable farming. Provide clear, concise, and structured JSON responses when requested."

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        return json.dumps({"error": f"AI service error: {str(e)}"})
