"""
Crop Disease Detection Route
==============================
Validates uploads, uses UUID temp filenames to prevent path traversal,
auto-cleans temp files, never exposes raw errors.
"""
import os
import json
import uuid
import time
import logging
from flask import Blueprint, request, jsonify
from services.crop_disease_service import analyze_crop_disease

logger = logging.getLogger(__name__)

crop_disease_bp = Blueprint("crop_disease", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE_MB = 4


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@crop_disease_bp.route("/api/v1/crops/detect-disease", methods=["POST"])
def detect_disease():
    """
    Detect Crop Disease using AI
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Upload crop image
    responses:
      200:
        description: Disease analysis result
    """
    image_path = None
    try:
        os.makedirs("temp", exist_ok=True)

        if 'image' not in request.files:
            return jsonify({"success": False, "message": "No image part in the request"}), 400

        image = request.files["image"]
        if image.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        if not _allowed_file(image.filename):
            return jsonify({"success": False, "message": "Invalid file type. Use JPG, PNG, or WebP."}), 400

        # UUID-based temp filename prevents path traversal
        ext = image.filename.rsplit(".", 1)[1].lower()
        safe_filename = f"{uuid.uuid4().hex}.{ext}"
        image_path = os.path.join("temp", safe_filename)

        start_time = time.time()
        logger.info(f"[VISION] Request received — saving as {safe_filename}")

        image.save(image_path)

        # Check file size after save
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            return jsonify({"success": False, "message": f"File too large ({file_size_mb:.1f}MB). Max {MAX_FILE_SIZE_MB}MB."}), 400

        result = analyze_crop_disease(image_path)

        elapsed = round(time.time() - start_time, 2)
        logger.info(f"[VISION] Gemini inference completed in {elapsed}s")

        # Intercept AI service busy or vision failure
        if "AI service busy" in result or "Vision analysis failed" in result or "unavailable" in result.lower():
            return jsonify({
                "success": False,
                "message": "🤖 AI assistant is busy. Please retry shortly.",
                "crop": "Unknown",
                "disease": "Unknown",
                "confidence": 0
            }), 200

        try:
            # Strip markdown if present
            clean_result = result.strip()
            if clean_result.startswith('```json'):
                clean_result = clean_result[len('```json'):]
            if clean_result.endswith('```'):
                clean_result = clean_result[:-3]
            clean_result = clean_result.strip()

            parsed_result = json.loads(clean_result)

            # Map remedies and preventions
            from core.organic_remedy_engine import generate_organic_remedy
            remedy_info = generate_organic_remedy(
                parsed_result.get("crop", "Unknown"),
                parsed_result.get("disease", "Unknown")
            )
            parsed_result["organic_remedies"] = remedy_info["organic_remedies"]
            parsed_result["prevention"] = remedy_info["prevention"]
            parsed_result["success"] = True

            return jsonify(parsed_result), 200
        except Exception:
            return jsonify({
                "success": False,
                "message": "🤖 Could not parse AI response. Please retry.",
                "crop": "Unknown",
                "disease": "Analysis error",
                "confidence": 0
            }), 200

    except Exception as e:
        logger.error(f"[VISION] Route error: {e}")
        return jsonify({
            "success": False,
            "message": "🤖 AI assistant is busy. Please retry shortly."
        }), 200
    finally:
        # Always clean up temp file
        if image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
            except Exception:
                pass
