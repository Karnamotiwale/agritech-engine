import os
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

        image_path = f"temp/{image.filename}"
        image.save(image_path)

        result = analyze_crop_disease(image_path)
        
        # Cleanup
        try:
            os.remove(image_path)
        except:
            pass

        return jsonify({
            "analysis": result
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
