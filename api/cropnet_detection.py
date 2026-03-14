from flask import Blueprint, request, jsonify
from services.crop_disease_service import analyze_crop_disease
import os
import json

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

    # Try to parse the result as JSON to ensure the format is valid and returned cleanly
    try:
        # Sometimes LLMs wrap JSON in ```json blocks
        if result.startswith("```json"):
            result = result[7:]
            if result.endswith("```"):
                result = result[:-3]
        parsed_result = json.loads(result)
        return jsonify({"analysis": parsed_result}), 200
    except json.JSONDecodeError:
        # Fallback to returning raw text inside the expected dictionary structure if JSON fails
        return jsonify({"analysis": result}), 200
