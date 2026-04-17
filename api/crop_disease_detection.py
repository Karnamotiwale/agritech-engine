import os
import json
from flask import Blueprint, request, jsonify
from services.crop_disease_service import analyze_crop_disease

crop_disease_bp = Blueprint("crop_disease", __name__)

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
        schema:
          type: object
          properties:
            analysis:
              type: string
    """
    try:
        # Check if temp dir exists
        os.makedirs("temp", exist_ok=True)
        
        if 'image' not in request.files:
            return jsonify({"error": "No image part in the request"}), 400
            
        image = request.files["image"]
        if image.filename == '':
            return jsonify({"error": "No selected file"}), 400
        # Logging initial receipt of request
        import time, logging
        logger = logging.getLogger(__name__)
        start_time = time.time()
        logger.info(f"[VISION API] Request received for {image.filename} - Started at {start_time}")
        
        image_path = f"temp/{image.filename}"
        image.save(image_path)

        result = analyze_crop_disease(image_path)
        
        # Logging TTFB boundary completion
        end_time = time.time()
        logger.info(f"[VISION API] Gemini inference completed in {round(end_time - start_time, 2)}s")
        
        # Cleanup
        try:
            os.remove(image_path)
        except:
            pass

        # Intercept AI service busy or vision failure
        if "AI service busy" in result or "Vision analysis failed" in result:
            return jsonify({
                "success": False,
                "message": "AI service busy. Please retry shortly.",
                "crop": "Error",
                "disease": "Error",
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
        except Exception as json_err:
            return jsonify({
                "success": False,
                "message": "Failed to parse AI response. Please retry.",
                "crop": "Unknown",
                "disease": "Analysis error",
                "confidence": 0,
                "raw": result
            }), 200
        
    except Exception as e:
        return jsonify({
            "success": False,
            "message": "AI service busy. Please retry shortly."
        }), 200
