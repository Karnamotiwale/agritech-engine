from flask import Blueprint, request, jsonify
from core.yield_prediction_engine import predict_yield

yield_bp = Blueprint('yield_prediction', __name__)

@yield_bp.route('/api/v1/crops/yield-prediction', methods=['POST'])
def yield_prediction():
    data = request.json or {}
    try:
        prediction = predict_yield(data)
        
        # Structure the response precisely for the frontend Yield Prediction UI
        return jsonify({
            "estimatedYield": f"{prediction['yield']} {prediction['unit']}",
            "yieldValue": prediction['yield'],
            "confidence": prediction['confidence'],
            "harvestWindow": prediction['harvest_window'],
            "summary": {
                "expectedYield": f"{prediction['yield']} {prediction['unit']}",
                "yieldRange": f"{prediction['yield'] * 0.9:.2f} - {prediction['yield'] * 1.1:.2f} Tons/Ha",
                "stability": "STABLE",
                "vsAverage": "N/A"
            },
            "factors": [],
            "risks": [],
            "explainability": {"confidence": prediction['confidence'], "reason": "Basic analytical math derivation applied."}
        }), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "An internal error occurred"}), 500
