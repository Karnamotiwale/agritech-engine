from core.yield_baseline import BASELINE_YIELD
from core.yield_feature_engine import build_yield_features
from core.gemini_service import ask_gemini
import json

def predict_yield(crop, journey):
    features = build_yield_features(journey)
    
    # Generate summary of conditions to send to AI
    stress_events = features.get("stress_events", 0)
    disease_events = features.get("disease_events", 0)
    irrigation_count = features.get("irrigation_count", 0)
    
    prompt = f"""
    Crop: {crop}
    History summary: {len(journey)} record logs.
    Irrigation events: {irrigation_count}
    Stress events: {stress_events}
    Disease events: {disease_events}
    
    Predict the yield per hectare based on this history.
    Respond STRICTLY with valid JSON without markdown tags.
    Format:
    {{
        "expected_yield_t_ha": float_value,
        "possible_risk_factors": ["risk 1", "risk 2"],
        "improvement_suggestions": ["advice 1", "advice 2"]
    }}
    """
    
    try:
        response_text = ask_gemini(prompt)
        response_text = response_text.replace("```json", "").replace("```", "").strip()
        result = json.loads(response_text)
        
        return {
            "expected_yield_t_ha": result.get("expected_yield_t_ha", 0),
            "confidence": "high" if stress_events == 0 else "medium",
            "drivers": features,
            "risk_factors": result.get("possible_risk_factors", []),
            "improvement_advice": result.get("improvement_suggestions", [])
        }
    except Exception as e:
        print(f"AI Yield Prediction Error: {e}")
        baseline = BASELINE_YIELD.get(crop, {"min": 2, "max": 5})

        # Start from mid baseline
        expected_yield = (baseline["min"] + baseline["max"]) / 2
        expected_yield += features.get("irrigation_count", 0) * 0.1
        expected_yield -= features.get("stress_events", 0) * 0.15
        expected_yield -= features.get("disease_events", 0) * 0.2

        # Clamp yield
        expected_yield = max(baseline["min"], min(expected_yield, baseline["max"]))

        confidence = "high"
        if features.get("stress_events", 0) > 2 or features.get("disease_events", 0) > 1:
            confidence = "medium"
        if features.get("stress_events", 0) > 4:
            confidence = "low"

        return {
            "expected_yield_t_ha": round(expected_yield, 2),
            "confidence": confidence,
            "drivers": features,
            "risk_factors": ["Fallback active (AI failure)"],
            "improvement_advice": ["Maintain optimal conditions"]
        }

