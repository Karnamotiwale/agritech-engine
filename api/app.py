from flask import Flask, request, jsonify
import pickle

# Core engines
from core.decision_engine import decide_action
from core.xai_engine import generate_explanation
from core.regret_engine import analyze_regret
from core.policy_engine import apply_penalty, get_policy_state
from core.rl_engine import update_q_table, get_q_table, get_state

app = Flask(__name__)

# Load trained ML model
with open("models/model.pkl", "rb") as f:
    model = pickle.load(f)

# -----------------------------------
# PREDICTION + DECISION + XAI
# -----------------------------------
@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    features = [[
        data["soil_moisture"],
        data["temperature"],
        data["humidity"],
        data["rain_forecast"]
    ]]

    # ML Prediction
    ml_prediction = model.predict(features)[0]

    # Hybrid Decision (Rules + Policy + RL)
    decision = decide_action(ml_prediction, data)

    # Explainable AI
    explanation = generate_explanation(
        data,
        ml_prediction,
        decision["decision"]
    )

    # Derive state for RL transparency
    state = get_state(data)

    return jsonify({
        "state": state,
        "ml_prediction": int(ml_prediction),
        "final_decision": decision["decision"],
        "explanation": explanation
    })


# -----------------------------------
# FEEDBACK + REGRET + RL LEARNING
# -----------------------------------
@app.route("/feedback", methods=["POST"])
def feedback():
    data = request.json

    decision = data["final_decision"]
    outcome = data["outcome"]
    state = data["state"]

    # Regret analysis
    regret_result = analyze_regret(decision, outcome)

    # Reward definition
    reward = -10 if regret_result["regret"] else 10

    # Reinforcement Learning update
    update_q_table(state, decision, reward)

    # Regret prevention (policy penalty)
    if regret_result["regret"]:
        apply_penalty(decision)

    return jsonify({
        "state": state,
        "final_decision": decision,
        "outcome": outcome,
        "reward": reward,
        "regret": regret_result["regret"],
        "reason": regret_result["reason"],
        "policy_state": get_policy_state(),
        "q_table": get_q_table()
    })


# -----------------------------------
# START SERVER (ALWAYS LAST)
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True)
