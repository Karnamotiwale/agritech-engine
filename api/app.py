# --------------------------------------------------
# CRITICAL: Load environment variables FIRST
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify
from flask_cors import CORS
import random

# --------------------------------------------------
# Advisory & Planning Engines
# --------------------------------------------------
from core.fertilizer_engine import recommend_fertilizer
from core.pest_disease_engine import generate_pest_disease_advisory
from core.irrigation_planner import plan_irrigation

# --------------------------------------------------
# Core AI Engines
# --------------------------------------------------
from core.ml_model import IrrigationMLModel
from core.decision_engine import decide_action
from core.regret_engine import calculate_regret
from core.rl_engine import update_q_table, get_q_values, get_state
from core.xai_engine import generate_explanation
from core.crop_rotation_engine import recommend_next_crop

# --------------------------------------------------
# Crop Tracing & Yield Engines
# --------------------------------------------------
from core.crop_trace_engine import log_crop_stage
from core.yield_prediction_engine import predict_yield
from core.supabase_client import supabase
from core.crop_constants import ALLOWED_CROPS, CROP_LIFECYCLES, validate_crop, safe_value

# --------------------------------------------------
# Flask app
# --------------------------------------------------
app = Flask(__name__)
# 1. Enable CORS for frontend
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}}, supports_credentials=True)

# 2. Global Error Handler - Force JSON responses
@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({
        "status": "error",
        "message": str(e)
    }), 500

# --------------------------------------------------
# LOAD ML MODEL ONCE
# --------------------------------------------------
try:
    ml_model = IrrigationMLModel()
except Exception as e:
    print(f"Warning: ML Model initialization issue: {e}")
    ml_model = None


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------
@app.route("/", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "AI engine is running"
    })


# --------------------------------------------------
# DECISION ENDPOINT (MAIN INTELLIGENCE)
# --------------------------------------------------
@app.route("/decide", methods=["POST"])
def decide():
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    # 0. Global Data Sanitization (Requirement 4)
    FIELDS_TO_SANITIZE = [
        "soil_moisture_pct", "rainfall_mm", "temperature_c", "humidity_pct",
        "nitrogen_kg_ha", "phosphorus_kg_ha", "potassium_kg_ha",
        "disease_risk_score", "pest_risk_score", "irrigation_applied_mm"
    ]
    for field in FIELDS_TO_SANITIZE:
        data[field] = safe_value(data.get(field))

    # Compatibility mapping for legacy engine logic
    data["disease_risk"] = "high" if data["disease_risk_score"] > 70 else "medium" if data["disease_risk_score"] > 30 else "low"
    data["pest_risk"] = "high" if data["pest_risk_score"] > 70 else "medium" if data["pest_risk_score"] > 30 else "low"

    try:
        crop = validate_crop(data.get("crop"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    # 1. ML Prediction
    ml_prediction = 0
    if ml_model:
        try:
            ml_prediction = ml_model.predict(data)
        except Exception:
            ml_prediction = 0

    # 2. Hybrid Decision (Rules + RL)
    decision_result = decide_action(ml_prediction, data)
    final_decision = decision_result["decision"]
    reason = decision_result["reason"]

    # 3. Explainable AI
    explanation = generate_explanation(
        data,
        ml_prediction,
        final_decision
    )

    # 4. RL Transparency
    state = get_state(data)
    q_values = get_q_values(state)

    # 5. Agronomy Advisories
    fertilizer_advice = recommend_fertilizer(data)
    pest_disease_advisory = generate_pest_disease_advisory(data)
    irrigation_plan = plan_irrigation(data, final_decision)

    # 6. Fetch crop journey so far (with error handling)
    journey_records = []
    try:
        response = (
            supabase
            .table("crop_trace_log")
            .select("*")
            .eq("crop", crop)
            .order("created_at")
            .execute()
        )
        journey_records = response.data if response and response.data else []
    except Exception as e:
        print(f"Supabase journey fetch failed: {e}")
        journey_records = []

    # 7. Yield trend prediction (with error handling)
    yield_trend = None
    try:
        if journey_records:
            yield_trend = predict_yield(crop, journey_records)
    except Exception as e:
        print(f"Yield prediction failed: {e}")
        yield_trend = None

    # 8. Log current stage (crop tracing) - fire and forget
    try:
        log_crop_stage(
            data=data,
            decision=final_decision,
            irrigation_plan=irrigation_plan,
            fertilizer=fertilizer_advice,
            pest_advice=pest_disease_advisory
        )
    except Exception as e:
        print(f"Crop trace logging failed: {e}")
        # Continue execution even if logging fails

    return jsonify({
        "state": state,
        "ml_prediction": int(ml_prediction),
        "final_decision": final_decision,
        "reason": reason,
        "explanation": explanation,
        "fertilizer_advice": fertilizer_advice,
        "pest_disease_advisory": pest_disease_advisory,
        "irrigation_plan": irrigation_plan,
        "yield_trend": yield_trend,
        "q_values": q_values
    })


# --------------------------------------------------
# FEEDBACK ENDPOINT (REGRET + RL LEARNING)
# --------------------------------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    body = request.json
    if not body:
        return jsonify({"error": "No input body"}), 400

    regret_score = calculate_regret(
        body["final_decision"],
        body["actual_outcome"],
        body["data"]
    )

    reward = 10.0 - (regret_score * 5.0)

    state = get_state(body["data"])
    update_q_table(
        state,
        body["final_decision"],
        reward,
        state
    )

    return jsonify({
        "status": "success",
        "regret_score": regret_score,
        "reward": reward
    })


# --------------------------------------------------
# CROP JOURNEY API (FULL TRACE)
# --------------------------------------------------
@app.route("/crop/journey", methods=["POST"])
def crop_journey():
    try:
        crop = validate_crop(request.json.get("crop"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not crop:
        return jsonify({"error": "Crop name required"}), 400

    records = (
        supabase
        .table("crop_trace_log")
        .select("*")
        .eq("crop", crop)
        .order("created_at")
        .execute()
    )

    return jsonify({
        "crop": crop,
        "journey": records.data
    })


# --------------------------------------------------
# CROP STAGES API (LIFECYCLE GUIDES)
# --------------------------------------------------
@app.route("/crop/stages", methods=["POST"])
def crop_stages():
    try:
        crop = validate_crop(request.json.get("crop"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    from core.crop_constants import CROP_LIFECYCLES
    stages = CROP_LIFECYCLES.get(crop, [])
    
    # Calculate statuses based on a hypothetical 'days_since_sowing' 
    # for demo purposes - in real app would use current date vs sowing date
    days_since_sowing = int(request.json.get("days_since_sowing", 0))
    
    formatted_stages = []
    current_stage = "Nursery" if crop == "rice" else "Germination"
    
    for s in stages:
        status = "upcoming"
        if days_since_sowing >= s["max_day"]:
            status = "completed"
        elif days_since_sowing >= s["min_day"]:
            status = "active"
            current_stage = s["name"]
        
        formatted_stages.append({
            "name": s["name"],
            "status": status,
            "days": f"{s['min_day']}-{s['max_day']}"
        })

    return jsonify({
        "crop": crop,
        "currentStage": current_stage,
        "stages": formatted_stages
    })


# --------------------------------------------------
# FINAL YIELD SNAPSHOT API
# --------------------------------------------------
@app.route("/yield/predict", methods=["POST"])
def yield_predict():
    try:
        crop = validate_crop(request.json.get("crop"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not crop:
        return jsonify({"error": "Crop required"}), 400

    records = (
        supabase
        .table("crop_trace_log")
        .select("*")
        .eq("crop", crop)
        .order("created_at")
        .execute()
    )

    return jsonify({
        "crop": crop,
        "yield_prediction": predict_yield(crop, records.data)
    })


# --------------------------------------------------
# AI HEALTH DETECTION ENDPOINT
# --------------------------------------------------
@app.route("/ai/health-detect", methods=["POST"])
def health_detect():
    """
    Disease detection endpoint that receives image URL and crop ID
    Returns mock disease detection results
    """
    data = request.json
    if not data:
        return jsonify({"error": "No input data provided"}), 400
    
    image_url = data.get("image_url")
    crop_id = data.get("crop_id")
    
    if not image_url:
        return jsonify({"error": "image_url is required"}), 400
    
    # Mock disease detection logic
    # In a real implementation, this would use ML model to analyze the image
    import random
    
    # Simulate different detection scenarios
    detection_scenarios = [
        {
            "status": "healthy",
            "issue": None,
            "severity": None,
            "solution": "Crop appears healthy. Continue regular monitoring and maintenance.",
            "prevention": "Maintain current practices. Ensure proper irrigation and nutrient management.",
            "confidence": 0.92
        },
        {
            "status": "diseased",
            "issue": "Leaf Blast (Fungal)",
            "severity": "moderate",
            "solution": "Apply Carbendazim 2g/L. Improve field drainage and reduce leaf wetness.",
            "prevention": "Use certified disease-free seeds. Avoid excessive nitrogen fertilization.",
            "confidence": 0.88
        },
        {
            "status": "diseased",
            "issue": "Bacterial Blight",
            "severity": "high",
            "solution": "Apply copper-based bactericide. Remove and destroy infected plants immediately.",
            "prevention": "Use resistant varieties. Ensure proper plant spacing for air circulation.",
            "confidence": 0.85
        },
        {
            "status": "stressed",
            "issue": "Nutrient Deficiency (Nitrogen)",
            "severity": "low",
            "solution": "Apply nitrogen-rich fertilizer (Urea 20-30 kg/ha). Monitor leaf color improvement.",
            "prevention": "Regular soil testing. Maintain balanced fertilization schedule.",
            "confidence": 0.90
        },
        {
            "status": "diseased",
            "issue": "Brown Spot Disease",
            "severity": "moderate",
            "solution": "Apply Mancozeb fungicide. Ensure balanced potassium fertilization.",
            "prevention": "Avoid water stress. Use disease-resistant varieties.",
            "confidence": 0.87
        }
    ]
    
    # Randomly select a scenario (weighted towards healthy for demo)
    rand = random.random()
    if rand < 0.4:  # 40% healthy
        result = detection_scenarios[0]
    else:  # 60% some issue
        result = random.choice(detection_scenarios[1:])
    
    return jsonify(result)


# --------------------------------------------------
# CROP ROTATION RECOMMENDATION (NEXT SEASON)
# --------------------------------------------------
@app.route("/crop/rotation", methods=["POST"])
def crop_rotation():
    try:
        crop = validate_crop(request.json.get("crop"))
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    if not crop:
        return jsonify({"error": "Crop required"}), 400

    records = (
        supabase
        .table("crop_trace_log")
        .select("*")
        .eq("crop", crop)
        .order("created_at")
        .execute()
    )

    if not records.data:
        return jsonify({"error": "No crop journey data available"}), 400

    recommendation = recommend_next_crop(crop, records.data)

    return jsonify({
        "status": "success",
        "rotation_recommendation": recommendation
    })


# --------------------------------------------------
# RECOMMENDATIONS ENDPOINT
# --------------------------------------------------
@app.route("/recommendations", methods=["GET"])
def get_recommendations():
    """
    Returns AI recommendations for a farm
    """
    try:
        farm_id = request.args.get("farm_id")
        if not farm_id:
            return jsonify({"error": "farm_id required"}), 400
        
        # Return empty recommendations for now
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# RL PERFORMANCE ENDPOINT
# --------------------------------------------------
@app.route("/ai/rl-performance", methods=["GET"])
def rl_performance():
    """
    Returns RL agent performance metrics
    """
    try:
        return jsonify({
            "overallScore": 0,
            "efficiencyTrend": "STABLE",
            "totalActions": 0,
            "positiveRewards": 0,
            "negativeRewards": 0,
            "lastUpdated": "2026-01-31T13:00:00Z"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# RL ACTIONS ENDPOINT
# --------------------------------------------------
@app.route("/ai/rl-actions", methods=["GET"])
def rl_actions():
    """
    Returns recent RL agent actions
    """
    try:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# RL REWARDS ENDPOINT
# --------------------------------------------------
@app.route("/ai/rl-rewards", methods=["GET"])
def rl_rewards():
    """
    Returns RL reward history
    """
    try:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# RL INSIGHTS ENDPOINT
# --------------------------------------------------
@app.route("/ai/rl-insights", methods=["GET"])
def rl_insights():
    """
    Returns RL learning insights
    """
    try:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# VALVES ENDPOINT
# --------------------------------------------------
@app.route("/valves", methods=["GET"])
def get_valves():
    """
    Returns valves for a crop
    """
    try:
        crop_id = request.args.get("crop_id")
        if not crop_id:
            return jsonify({"error": "crop_id required"}), 400
        
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# VALVE TOGGLE ENDPOINT
# --------------------------------------------------
@app.route("/valves/toggle", methods=["POST"])
def toggle_valve():
    """
    Toggles a valve on/off
    """
    try:
        data = request.json
        valve_id = data.get("valve_id")
        active = data.get("active")
        
        if not valve_id:
            return jsonify({"error": "valve_id required"}), 400
        
        return jsonify({
            "id": valve_id,
            "isActive": active,
            "status": "RUNNING" if active else "IDLE"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# VALVE OVERRIDE ENDPOINT
# --------------------------------------------------
@app.route("/valves/override", methods=["POST"])
def override_valve():
    """
    Overrides valve schedule
    """
    try:
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# GROWTH STAGES ENDPOINT (alias for /crop/stages)
# --------------------------------------------------
@app.route("/crop/growth-stages", methods=["POST"])
def growth_stages():
    """
    Returns crop growth stages
    """
    try:
        data = request.json
        crop = validate_crop(data.get("crop"))
        
        return jsonify({
            "currentStage": "Unknown",
            "stages": []
        })
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# DETAILED ADVISORY ENDPOINT
# --------------------------------------------------
@app.route("/ai/detailed-advisory", methods=["GET"])
def detailed_advisory():
    """
    Returns detailed AI advisory for a crop
    """
    try:
        return jsonify({
            "fertilizer": {"status": "OPTIMAL", "dosage": "N/A", "timing": "N/A", "method": "N/A"},
            "pesticide": {"detected": False, "riskLevel": "NONE", "productName": "N/A", "category": "N/A", "target": "N/A", "dosage": "N/A", "safetyInterval": "N/A"},
            "explainability": {"reason": "Conditions stable", "factors": [], "confidence": 1.0}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# YIELD PREDICTION ENDPOINT
# --------------------------------------------------
@app.route("/yield/prediction", methods=["GET"])
def yield_prediction():
    """
    Returns AI yield prediction for a crop
    """
    try:
        return jsonify({
            "summary": {"expectedYield": "0 kg", "yieldRange": "0-0 kg", "vsAverage": "0%", "stability": "STABLE", "trend": "STABLE"},
            "risks": [],
            "factors": [],
            "explainability": {"reason": "Awaiting data", "confidence": 1.0}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# RESOURCE ANALYTICS ENDPOINT
# --------------------------------------------------
@app.route("/resource/analytics", methods=["GET"])
def resource_analytics():
    """
    Returns AI resource analytics for a crop
    """
    try:
        return jsonify({
            "water": {"totalUsed": "0L", "efficiencyScore": 1.0, "status": "OPTIMAL", "breakdown": {"rain": 0, "irrigation": 0}, "comparison": {"used": 0, "required": 0, "unit": "L"}},
            "fertilizer": {"totalUsed": "0 kg", "efficiencyScore": 1.0, "status": "OPTIMAL", "breakdown": []},
            "storage": {"waterLevel": 0, "fertilizerStock": "0 kg", "daysRemaining": 0},
            "insights": {"efficiencyImpact": "N/A", "environmentalScore": 100, "wastageReduction": "0%"}
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# AI VALVE SCHEDULE ENDPOINT
# --------------------------------------------------
@app.route("/ai/valves", methods=["POST"])
def ai_valve_schedule():
    """
    Generates AI valve schedules
    """
    try:
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# SENSOR ENDPOINTS
# --------------------------------------------------
@app.route("/sensors", methods=["GET"])
def get_sensors():
    """
    Returns current sensor readings for a crop
    """
    try:
        crop_id = request.args.get("crop_id")
        return jsonify({
            "moisture": 62.5,
            "ph": 6.8,
            "n": 120,
            "p": 45,
            "k": 60,
            "npk": "120-45-60"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sensors/tick", methods=["GET"])
def tick_sensors():
    """
    Simulates real-time sensor updates
    """
    try:
        crop_id = request.args.get("crop_id")
        # Vary moisture and pH slightly
        return jsonify({
            "moisture": 62.5 + (random.random() * 2 - 1),
            "ph": 6.8 + (random.random() * 0.2 - 0.1),
            "n": 120,
            "p": 45,
            "k": 60,
            "npk": "120-45-60"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# CROP HISTORY ENDPOINT
# --------------------------------------------------
@app.route("/crop/history", methods=["GET"])
def get_crop_history():
    """
    Returns full history for a crop from the trace log
    """
    try:
        crop_id = request.args.get("crop_id")
        if not crop_id:
            return jsonify({"error": "crop_id required"}), 400
            
        # For demo purposes, we'll try to match by crop name or use a sample
        # In a real app, this would be a specific query
        records = (
            supabase
            .table("crop_trace_log")
            .select("*")
            .limit(20)
            .execute()
        )
        return jsonify(records.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --------------------------------------------------
# RUN SERVER
# --------------------------------------------------
@app.route("/crop/rotation", methods=["POST"])
def crop_rotation():
    try:
        data = request.json
        return jsonify({
            "rotation_recommendation": {
                "recommended_crop": "Pulses",
                "reason": "Nitrogen fixation required after Rice cultivation.",
                "benefits": ["Restores Soil Nitrogen", "Breaks Pest Cycles", "Low Water Usage"]
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/yield/predict", methods=["POST"])
def yield_predict():
    try:
        data = request.json
        return jsonify({
            "yield_prediction": {
                "summary": {
                    "expectedYield": "4,250 kg/ha",
                    "stability": "STABLE",
                    "vsAverage": "+12%"
                }
            }
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
