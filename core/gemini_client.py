"""
KisaanSaathi — Production Gemini AI Client
============================================
Centralized, fault-tolerant wrapper for all Google Gemini API calls.

Design:
  - Single shared client, NO global threading lock (prevents cascading timeouts)
  - Max 1 retry with 2s delay on 429/503 errors only
  - Graceful string fallbacks — callers never see exceptions
  - Structured logging via Python logging module
"""
import os
import time
import logging
from dotenv import load_dotenv

load_dotenv()

from google import genai

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# CLIENT SINGLETON
# ---------------------------------------------------------------------------
_client = None

PRIMARY_MODEL = "gemini-1.5-flash"
FALLBACK_MODEL = "gemini-2.0-flash"
VISION_MODEL = "gemini-1.5-flash"

def get_client():
    """Lazy-initialise the Gemini SDK client."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.warning("GEMINI_API_KEY is not set — all AI features disabled.")
            return None
        try:
            _client = genai.Client(api_key=api_key)
            logger.info("Gemini client initialised successfully.")
        except Exception as e:
            logger.error(f"Failed to initialise Gemini client: {e}")
    return _client


# ---------------------------------------------------------------------------
# INTERNAL CALLER WITH RETRY (max 1 retry, short delays)
# ---------------------------------------------------------------------------
def _safe_generate(client, model: str, contents, fallback_model: str = None):
    """
    Call Gemini with at most 1 retry on transient errors (429/503).
    Falls back to fallback_model if primary model is overloaded.
    Returns response text or a safe fallback string — NEVER raises.
    """
    max_retries = 1
    last_error = None

    for attempt in range(max_retries + 1):
        current_model = model if attempt == 0 else (fallback_model or model)
        try:
            logger.info(f"[Gemini] Calling model={current_model} (attempt {attempt + 1})")
            start = time.time()
            response = client.models.generate_content(
                model=current_model,
                contents=contents,
            )
            elapsed = round(time.time() - start, 2)
            logger.info(f"[Gemini] Response received in {elapsed}s")
            return response.text

        except Exception as e:
            last_error = e
            err_str = str(e).lower()
            is_transient = any(k in err_str for k in ["429", "503", "quota", "overloaded", "unavailable", "resource"])

            if is_transient and attempt < max_retries:
                delay = 2
                logger.warning(f"[Gemini] Transient error: {e}. Retrying in {delay}s with model={fallback_model or model}...")
                time.sleep(delay)
            else:
                logger.error(f"[Gemini] Final failure: {e}")
                break

    # Never raise — always return safe fallback
    return None


# ---------------------------------------------------------------------------
# PUBLIC API: ask_text
# ---------------------------------------------------------------------------
def ask_gemini(prompt: str) -> str:
    """
    Text-only Gemini call.
    Used by: chatbot, advisory, sustainability, alert engine.
    Returns a string — always safe to show to users.
    """
    client = get_client()
    if not client:
        return "🤖 AI assistant is temporarily offline. Please try again shortly."

    result = _safe_generate(client, model=PRIMARY_MODEL, contents=prompt, fallback_model=FALLBACK_MODEL)
    if result is None:
        return "🤖 AI assistant is busy right now. Please try again in a moment."
    return result


def generate_ai_response(prompt: str, image=None) -> str:
    """
    General-purpose Gemini caller. Supports optional image.
    """
    client = get_client()
    if not client:
        return "AI service temporarily unavailable (API key missing)"

    model = VISION_MODEL if image else PRIMARY_MODEL
    contents = [prompt]
    if image:
        contents.append(image)

    result = _safe_generate(client, model=model, contents=contents, fallback_model=FALLBACK_MODEL)
    if result is None:
        return "AI service busy. Please retry shortly."
    return result


# ---------------------------------------------------------------------------
# PUBLIC API: analyze_image (Vision)
# ---------------------------------------------------------------------------
def analyze_image(prompt: str, image_path: str) -> str:
    """
    Vision analysis for crop disease detection.
    Validates file → opens with PIL → sends to Gemini.
    Returns a string — always safe, never raises.
    """
    client = get_client()
    if not client:
        return "Vision analysis failed: API key missing"

    # --- File validation ---
    if not os.path.exists(image_path):
        return "Vision analysis failed: Image file not found"

    file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
    if file_size_mb > 4:
        return "Vision analysis failed: File too large (max 4MB)"

    # --- Image loading & compression ---
    import PIL.Image
    try:
        img = PIL.Image.open(image_path)
        img.verify()
        img = PIL.Image.open(image_path)  # Reopen after verify

        # Resize large images to prevent slow uploads
        max_dim = 1024
        if img.width > max_dim or img.height > max_dim:
            img.thumbnail((max_dim, max_dim), PIL.Image.LANCZOS)
            logger.info(f"[Vision] Image resized to {img.size}")

    except Exception as e:
        return f"Vision analysis failed: Invalid image format ({str(e)})"

    # --- Call Gemini ---
    logger.info(f"[Vision] Analyzing {image_path} ({file_size_mb:.1f}MB)...")
    start = time.time()

    result = _safe_generate(client, model=VISION_MODEL, contents=[prompt, img], fallback_model=FALLBACK_MODEL)

    elapsed = round(time.time() - start, 2)
    logger.info(f"[Vision] Completed in {elapsed}s")

    if result is None:
        return "Vision analysis failed: AI service busy. Please retry shortly."
    return result
