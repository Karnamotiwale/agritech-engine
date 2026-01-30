from core.policy_engine import is_action_allowed
from core.rl_engine import choose_action, get_state


def decide_action(ml_prediction, data):
    """
    Decide whether irrigation is required (1 = Yes, 0 = No)

    data: dict with keys matching farm_data.csv columns
    """

    # Build RL state from data
    state = get_state(data)

    # RL suggested action (0 or 1)
    rl_action = choose_action(state)

    # ---------------- RULE-BASED OVERRIDES ----------------

    # RULE 1: Heavy rainfall → no irrigation
    if data["rainfall_mm"] >= 80:
        return {
            "decision": 0,
            "reason": "Recent heavy rainfall detected"
        }

    # RULE 2: Soil moisture already sufficient
    if data["soil_moisture_pct"] >= 65:
        return {
            "decision": 0,
            "reason": "Soil moisture is sufficient"
        }

    # RULE 3: Crop-specific safety rules
    if data["crop"] == "pulses" and data["soil_moisture_pct"] > 60:
        return {
            "decision": 0,
            "reason": "Pulses are sensitive to waterlogging"
        }

    # RULE 4: Critical growth stages favor irrigation
    critical_stages = [
        "transplanting",
        "tillering",
        "panicle_initiation",
        "flowering",
        "cri",
        "tasseling",
        "silking"
    ]

    if data["growth_stage"] in critical_stages:
        if is_action_allowed(rl_action, data):
            return {
                "decision": rl_action,
                "reason": f"Critical growth stage: {data['growth_stage']}"
            }

    # ---------------- RL DECISION ----------------

    if is_action_allowed(rl_action, data):
        return {
            "decision": rl_action,
            "reason": "RL policy selected action"
        }

    # ---------------- FALLBACK ----------------

    return {
        "decision": int(ml_prediction),
        "reason": "Fallback to ML prediction"
    }
