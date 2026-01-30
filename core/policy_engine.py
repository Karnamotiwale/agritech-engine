from core.supabase_client import supabase

TABLE_NAME = "policy_penalties"



# --------------------------------------------------
# MAIN POLICY FUNCTION
# --------------------------------------------------
def is_action_allowed(action, data):
    """
    Persistent policy engine.

    action: 0 (do not irrigate) | 1 (irrigate)
    data: dict with farm_data.csv fields

    Returns:
        True  -> action allowed
        False -> action blocked (penalty recorded)
    """

    # If no irrigation requested → always allowed
    if action == 0:
        return True

    crop = data["crop"]
    growth_stage = data["growth_stage"]
    soil_moisture = data["soil_moisture_pct"]
    rainfall = data["rainfall_mm"]
    disease_risk = data["disease_risk"]
    pest_risk = data["pest_risk"]

    # ---------------- RULE 1: HEAVY RAIN ----------------
    if rainfall >= 80:
        _log_penalty(
            data, action,
            penalty=2.0,
            rule="RAIN_BLOCK_RULE",
            explanation="Heavy rainfall detected; irrigation blocked."
        )
        return False

    # ---------------- RULE 2: EXCESS SOIL MOISTURE ----------------
    if soil_moisture >= 70:
        _log_penalty(
            data, action,
            penalty=1.5,
            rule="HIGH_SOIL_MOISTURE",
            explanation="Soil moisture already sufficient."
        )
        return False

    # ---------------- RULE 3: PULSES WATERLOGGING ----------------
    if crop == "pulses" and soil_moisture > 60:
        _log_penalty(
            data, action,
            penalty=2.5,
            rule="PULSES_WATERLOGGING_RULE",
            explanation="Pulses are sensitive to waterlogging."
        )
        return False

    # ---------------- RULE 4: DISEASE RISK ----------------
    if disease_risk == "high":
        _log_penalty(
            data, action,
            penalty=3.0,
            rule="DISEASE_IRRIGATION_BLOCK",
            explanation="High disease risk; irrigation may increase spread."
        )
        return False

    # ---------------- RULE 5: CROP-SPECIFIC LIMITS ----------------
    if crop == "wheat" and soil_moisture > 65:
        _log_penalty(
            data, action,
            penalty=1.2,
            rule="WHEAT_OVER_IRRIGATION",
            explanation="Soil moisture above safe limit for wheat."
        )
        return False

    if crop == "maize" and soil_moisture > 65:
        _log_penalty(
            data, action,
            penalty=1.2,
            rule="MAIZE_OVER_IRRIGATION",
            explanation="Soil moisture above safe limit for maize."
        )
        return False

    if crop == "sugarcane" and soil_moisture > 80:
        _log_penalty(
            data, action,
            penalty=1.0,
            rule="SUGARCANE_EXCESS_MOISTURE",
            explanation="Sugarcane does not require irrigation at this moisture."
        )
        return False

    # ---------------- DEFAULT: ALLOWED ----------------
    return True


# --------------------------------------------------
# INTERNAL: LOG PENALTY TO SUPABASE
# --------------------------------------------------
def _log_penalty(data, action, penalty, rule, explanation):
    """
    Persist policy violation into Supabase.
    """

    supabase.table(TABLE_NAME).insert({
        "crop": data["crop"],
        "growth_stage": data["growth_stage"],
        "soil_moisture_pct": data["soil_moisture_pct"],
        "rainfall_mm": data["rainfall_mm"],
        "disease_risk": data["disease_risk"],
        "pest_risk": data["pest_risk"],
        "action": action,
        "allowed": False,
        "penalty_score": penalty,
        "policy_rule": rule,
        "explanation": explanation
    }).execute()


