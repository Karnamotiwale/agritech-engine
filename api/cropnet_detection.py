from flask import Blueprint, request, jsonify  # type: ignore
from services.crop_disease_service import analyze_crop_disease  # type: ignore
from core.response_formatter import short_response
import os

cropnet_bp = Blueprint("cropnet_bp", __name__)

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
        schema:
          type: object
          properties:
            disease:
              type: string
            symptoms:
              type: string
            treatment:
              type: string
            prevention:
              type: string
    """
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]
    if image.filename == '':
        return jsonify({"error": "No selected file"}), 400

    temp_path = f"temp_{image.filename}"
    image.save(temp_path)

    result = analyze_crop_disease(temp_path)

    try:
        os.remove(temp_path)
    except:
        pass

    short_text = short_response(result)
    return jsonify({"message": short_text}), 200
