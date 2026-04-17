"""
CropNet Disease Detection (CNN alternate route)
=================================================
Uses Gemini Vision via centralized client.
Validates uploads, intercepts AI failures, never crashes.
"""
from flask import Blueprint, request, jsonify
from services.crop_disease_service import analyze_crop_disease
from core.response_formatter import short_response
import os
import logging

logger = logging.getLogger(__name__)

cropnet_bp = Blueprint("cropnet_bp", __name__)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}


def _allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@cropnet_bp.route("/api/v1/crops/detect-disease-cnn", methods=["POST"])
def cropnet_detect():
    """
    AI Crop Disease Detection using Gemini Vision
    ---
    tags:
      - AI Vision

    consumes:
      - multipart/form-data

    parameters:
      - name: image
        in: formData
        type: file
        required: true
        description: Upload crop leaf image

    responses:
      200:
        description: AI disease detection result
    """
    try:
        if "image" not in request.files:
            return jsonify({"success": False, "message": "No image uploaded"}), 400

        image = request.files["image"]
        if image.filename == '':
            return jsonify({"success": False, "message": "No selected file"}), 400

        if not _allowed_file(image.filename):
            return jsonify({"success": False, "message": "Invalid file type. Use JPG, PNG, or WebP."}), 400

        os.makedirs("temp", exist_ok=True)
        temp_path = f"temp/{image.filename}"
        image.save(temp_path)

        result = analyze_crop_disease(temp_path)

        try:
            os.remove(temp_path)
        except Exception:
            pass

        # Intercept AI service busy or vision failure
        if "AI service busy" in result or "Vision analysis failed" in result or "unavailable" in result.lower():
            return jsonify({
                "success": False,
                "message": "🤖 AI assistant is busy. Please retry shortly."
            }), 200

        short_text = short_response(result)
        return jsonify({"success": True, "message": short_text}), 200

    except Exception as e:
        logger.error(f"[CropNet] Route error: {e}")
        return jsonify({
            "success": False,
            "message": "🤖 AI assistant is busy. Please retry shortly."
        }), 200
