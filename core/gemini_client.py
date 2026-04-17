import os
from dotenv import load_dotenv
import threading
import time

load_dotenv()

# The new official SDK
from google import genai
from google.genai import types

_client = None

def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("Warning: GEMINI_API_KEY is not set. Gemini features will be disabled.")
            return None
        try:
            _client = genai.Client(api_key=api_key)
        except Exception as e:
            print(f"Warning: Failed to initialize Gemini API: {e}")
    return _client

gemini_lock = threading.Lock()
last_call_time = 0
MIN_DELAY = 2

def generate_ai_response(prompt, image=None):
    """
    Centralized Gemini caller using google-genai.
    """
    global last_call_time
    
    client = get_client()
    if not client:
        return "AI service temporarily unavailable (API key missing)"

    with gemini_lock:
        now = time.time()
        if now - last_call_time < MIN_DELAY:
            time.sleep(MIN_DELAY - (now - last_call_time))
            
        last_call_time = time.time()

        try:
            model_name = "gemini-pro-latest" if image else "gemini-flash-latest"
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
    
    client = get_client()
    if not client:
        return "AI advisory service temporarily unavailable (API key missing)."
        
    with gemini_lock:
        now = time.time()
        if now - last_call_time < MIN_DELAY:
            time.sleep(MIN_DELAY - (now - last_call_time))
            
        last_call_time = time.time()
        
        try:
            response = client.models.generate_content(
                model="gemini-flash-latest",
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
    import logging
    logger = logging.getLogger(__name__)

    client = get_client()
    if not client:
        return "Vision analysis failed: API key missing"
        
    try:
        if not os.path.exists(image_path):
            return "Vision analysis failed: Image file not found"
            
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > 5:
            return "Vision analysis failed: File too large (max 5MB)"
            
        import PIL.Image
        try:
            img = PIL.Image.open(image_path)
            # Validate it's an image
            img.verify()
            img = PIL.Image.open(image_path) # Reopen after verify
        except Exception as e:
            return f"Vision analysis failed: Invalid image format ({str(e)})"
            
        # Using Google GenAI SDK direct embedded image support (no upload API required)
        logger.info(f"Analyzing {image_path} with Gemini directly...")
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, img]
        )
        return response.text
    except Exception as e:
        logger.error(f"Gemini Vision API error: {str(e)}")
        return f"Vision analysis failed: {str(e)}"

