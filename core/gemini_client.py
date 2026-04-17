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

def with_retry(max_retries=1, base_delay=1, max_delay=3):
    """
    Exponential backoff retry decorator for Gemini API calls.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    err_str = str(e)
                    # Only retry on 503 or 429 quota/overload errors
                    if "429" in err_str or "503" in err_str or "quota" in err_str.lower() or "overloaded" in err_str.lower() or "unavailable" in err_str.lower():
                        if retries == max_retries:
                            print(f"[Gemini] Max retries reached for {func.__name__}. Error: {e}")
                            break
                        delay = min(base_delay * (2 ** retries), max_delay)
                        print(f"[Gemini] Error {e}. Retrying in {delay}s... ({retries+1}/{max_retries})")
                        time.sleep(delay)
                        retries += 1
                    else:
                        print(f"[Gemini] Unrecoverable error in {func.__name__}: {e}")
                        break
            # Fallback strings if all retries fail or an unhandled exception occurred
            if "analyze_image" in func.__name__:
                return "Vision analysis failed: AI service busy. Please retry shortly."
            return "AI service busy. Please retry shortly."
        return wrapper
    return decorator

@with_retry()
def _call_generate_content(client, model, contents):
    """Inner core strictly for generation, isolated for retry loops."""
    # Enforcing API timeout within HTTP client inside SDK is tricky, relying on outer wrapper timeouts
    return client.models.generate_content(model=model, contents=contents).text

def generate_ai_response(prompt, image=None):
    """
    Centralized Gemini caller using google-genai.
    """
    client = get_client()
    if not client:
        return "AI service temporarily unavailable (API key missing)"

    with gemini_lock:
        try:
            model_name = "gemini-1.5-pro" if image else "gemini-1.5-flash"
            contents = [prompt]
            if image:
                contents.append(image)
                
            return _call_generate_content(client, model=model_name, contents=contents)
        except Exception as e:
            print("Gemini error:", e)
            return "AI service busy. Please retry shortly."

def ask_gemini(prompt):
    """
    Used primarily by the chatbot and advisory endpoints.
    """
    client = get_client()
    if not client:
        return "AI advisory service temporarily unavailable (API key missing)."
        
    with gemini_lock:
        try:
            return _call_generate_content(client, model="gemini-1.5-flash", contents=prompt)
        except Exception as e:
            print("Gemini Error:", e)
            return "AI service busy. Please retry shortly."

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
            
        logger.info(f"Analyzing {image_path} with Gemini directly...")
        
        # Wrapped for retries natively inside _call_generate_content
        return _call_generate_content(client, model="gemini-1.5-flash", contents=[prompt, img])
    except Exception as e:
        logger.error(f"Gemini Vision API error: {str(e)}")
        return "Vision analysis failed: AI service busy. Please retry shortly."

