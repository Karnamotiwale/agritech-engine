from flask import Blueprint, request, jsonify
from core.yield_prediction_engine import predict_yield

yield_bp = Blueprint('yield_prediction', __name__)

@yield_bp.route('/yieldPrediction', methods=['POST'])
def yield_prediction():
    """
    Predict Crop Yield
    ---
    tags:
      - Prediction
    parameters:
      - in: body
        name: body
        schema:
          type: object
    responses:
      200:
        description: Successful response
    """
    data = request.json or {}
    try:
        crop = data.get("crop", "unknown")
        # Ensure journey exists for feature builder
        journey = data.get("journey", []) 
        
        # we can inject data features safely into journey format if empty
        if not journey:
            journey = [data]
            
        prediction = predict_yield(crop, journey)
        return jsonify(prediction), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
