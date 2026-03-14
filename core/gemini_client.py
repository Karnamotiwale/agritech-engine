import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()

# The new official SDK
from google import genai
from google.genai import types

# Ensure API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("Warning: GEMINI_API_KEY is not set. Gemini features will be disabled.")

# Initialize the new genai client correctly
client = genai.Client(api_key=api_key) if api_key else None

gemini_lock = threading.Lock()
last_call_time = 0
MIN_DELAY = 2

def generate_ai_response(prompt, image=None):
    """
    Centralized Gemini caller using google-genai.
    """
    global last_call_time
    
    if not client:
        return "AI service temporarily unavailable (API key missing)"

    with gemini_lock:
        now = time.time()
        if now - last_call_time < MIN_DELAY:
            time.sleep(MIN_DELAY - (now - last_call_time))
            
        last_call_time = time.time()

        try:
            model_name = "gemini-1.5-pro" if image else "gemini-1.5-flash"
            contents = [prompt]
            if image:
                contents.append(image)
                
            response = client.models.generate_content(
                model=model_name,
                contents=contents
            )
            return response.text
        except Exception as e:
            print("Gemini error:", e)
            return "AI service temporarily unavailable"

def ask_gemini(prompt):
    """
    Used primarily by the chatbot and advisory endpoints.
    """
    global last_call_time
    
    if not client:
        return "AI advisory service temporarily unavailable (API key missing)."
        
    with gemini_lock:
        now = time.time()
        if now - last_call_time < MIN_DELAY:
            time.sleep(MIN_DELAY - (now - last_call_time))
            
        last_call_time = time.time()
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
        except Exception as e:
            print("Gemini Error:", e)
            return "AI advisory service temporarily unavailable."

# --------------------------------------------------
# VISION ANALYSIS FUNCTION
# --------------------------------------------------

def analyze_image(prompt, image_path):
    """
    Used by the crop disease detection endpoints.
    """
    if not client:
        return "Vision analysis failed: API key missing"
        
    # No lock required specifically for this as it's synchronous upload
    try:
        # With the new google-genai, we can upload files using client.files.upload
        myfile = client.files.upload(file=image_path)
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, myfile]
        )
        return response.text
    except Exception as e:
        return f"Vision analysis failed: {str(e)}"

