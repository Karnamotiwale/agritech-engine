# --------------------------------------------------
# CRITICAL: Load environment variables FIRST
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, jsonify

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
from core.crop_stage_guide import CROP_STAGE_GUIDE
from core.yield_prediction_engine import predict_yield
from core.supabase_client import supabase

# --------------------------------------------------
# Flask app
# --------------------------------------------------
app = Flask(__name__)

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

    crop = data["crop"]

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

    # 6. Fetch crop journey so far
    journey_records = (
        supabase
        .table("crop_trace_log")
        .select("*")
        .eq("crop", crop)
        .order("created_at")
        .execute()
    ).data

    # 7. Yield trend prediction (based on journey so far)
    yield_trend = None
    if journey_records:
        yield_trend = predict_yield(crop, journey_records)

    # 8. Log current stage (crop tracing)
    log_crop_stage(
        data=data,
        decision=final_decision,
        irrigation_plan=irrigation_plan,
        fertilizer=fertilizer_advice,
        pest_advice=pest_disease_advisory
    )

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
    crop = request.json.get("crop")
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
# FINAL YIELD SNAPSHOT API
# --------------------------------------------------
@app.route("/yield/predict", methods=["POST"])
def yield_predict():
    crop = request.json.get("crop")
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
# CROP ROTATION RECOMMENDATION (NEXT SEASON)
# --------------------------------------------------
@app.route("/crop/rotation", methods=["POST"])
def crop_rotation():
    crop = request.json.get("crop")
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
# START SERVER (ALWAYS LAST)
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
