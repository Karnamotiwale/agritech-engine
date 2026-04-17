from flask import Blueprint, request, jsonify
from core.decision_engine import decide_action
from core.ml_model import IrrigationMLModel

ai_decision_bp = Blueprint('ai_decision', __name__)

# Preload ML model to avoid loading on every request
try:
    ml_model = IrrigationMLModel()
except Exception as e:
    print(f"Failed to load ML model: {e}")
    ml_model = None

@ai_decision_bp.route('/api/v1/ai/irrigation-decision', methods=['POST'])
def irrigation_decision():
    """
    Irrigation AI prediction
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
    responses:
      200:
        description: Irrigation decision and prediction
    """
    data = request.json or {}
    
    # Inject safe defaults for ML/RL to prevent crashes
    safe_data = {
        "crop": data.get("crop", "wheat"),
        "growth_stage": data.get("growth_stage", "Vegetative"),
        "soil_moisture_pct": float(data.get("soil_moisture_pct", 50.0)),
        "temperature_c": float(data.get("temperature_c", 25.0)),
        "humidity_pct": float(data.get("humidity_pct", 60.0)),
        "rainfall_mm": float(data.get("rainfall_mm", 0.0)),
        "soil_ph": float(data.get("soil_ph", 7.0)),
        "nitrogen_kg_ha": float(data.get("nitrogen_kg_ha", 50.0)),
        "phosphorus_kg_ha": float(data.get("phosphorus_kg_ha", 50.0)),
        "potassium_kg_ha": float(data.get("potassium_kg_ha", 50.0)),
        "disease_risk": data.get("disease_risk", "low"),
        "pest_risk": data.get("pest_risk", "low")
    }

    try:
        ml_prediction = 0
        if ml_model:
            try:
                ml_prediction = ml_model.predict(safe_data)
            except Exception as e:
                print(f"ML Model error: {e}")
                
        decision = decide_action(ml_prediction, safe_data)
        return jsonify(decision), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred"}), 500
