from core.policy_engine import is_action_allowed
from core.rl_engine import choose_action, get_state

def decide_action(ml_prediction, data):
    state = get_state(data)

    # RL suggested action
    rl_action = choose_action(state)

    # RULE 1: Rain forecast blocks irrigation
    if data["rain_forecast"] == 1:
        return {
            "decision": 0,
            "reason": "Rain forecast detected"
        }

    # RULE 2: Soil moisture sufficient
    if data["soil_moisture"] > 50:
        return {
            "decision": 0,
            "reason": "Soil moisture sufficient"
        }

    # RL preferred action (if allowed)
    if is_action_allowed(rl_action):
        return {
            "decision": rl_action,
            "reason": f"RL policy selected action {rl_action}"
        }

    # Fallback to ML
    return {
        "decision": ml_prediction,
        "reason": "Fallback to ML prediction"
    }
