import os
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai
import threading
import time

# Ensure API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY is not set. Gemini features will be disabled.")

# Configure Gemini once globally
genai.configure(api_key=api_key)

# We use gemini-1.5-flash as the default model per requirements
model = genai.GenerativeModel("gemini-1.5-flash")

# We can specify gemini-1.5-pro for vision if needed, but 1.5-flash also supports vision reasonably well.
# We will use what's requested, but allow overriding the model if image is passed.
vision_model = genai.GenerativeModel("gemini-1.5-pro")

gemini_lock = threading.Lock()
last_call_time = 0
MIN_DELAY = 2

def generate_ai_response(prompt, image=None):
    """
    Centralized Gemini caller.
    Enforces a global lock so only one request happens at a time.
    Enforces a minimum delay between requests to avoid quota exhaustion.
    Includes fallback logic to never crash the backend.
    """
    global last_call_time
    
    if not api_key:
        return "AI service temporarily unavailable (API key missing)"

    with gemini_lock:
        now = time.time()
        if now - last_call_time < MIN_DELAY:
            time.sleep(MIN_DELAY - (now - last_call_time))
            
        last_call_time = time.time()

        try:
            if image:
                response = vision_model.generate_content([prompt, image])
            else:
                response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            print("Gemini error:", e)
            return "AI service temporarily unavailable"

def ask_gemini(prompt):
    global last_call_time
    
    if not api_key:
        return "AI advisory service temporarily unavailable (API key missing)."
        
    with gemini_lock:
        now = time.time()
        if now - last_call_time < MIN_DELAY:
            time.sleep(MIN_DELAY - (now - last_call_time))
            
        last_call_time = time.time()
        
        try:
            # For this we use gemini-2.5-flash as specified in prompt, but we'll use 1.5 because 2.5 is not accessible in genai directly or uses same name. Wait, the prompt specifically said "gemini-2.5-flash". We will use exactly what was requested.
            model_2_5 = genai.GenerativeModel("gemini-2.5-flash")
            response = model_2_5.generate_content(prompt)
            return response.text
        except Exception as e:
            print("Gemini Error:", e)
            return "AI advisory service temporarily unavailable."

# --------------------------------------------------
# NEW VISION ANALYSIS FUNCTION
# --------------------------------------------------
vision_model_2_5 = genai.GenerativeModel("gemini-2.5-flash")

def analyze_image(prompt, image_path):
    try:
        with open(image_path, "rb") as img:
            response = vision_model_2_5.generate_content(
                [
                    prompt,
                    {"mime_type": "image/jpeg", "data": img.read()}
                ]
            )
        return response.text
    except Exception as e:
        return f"Vision analysis failed: {str(e)}"
