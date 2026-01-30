def calculate_regret(action_taken, actual_outcome, data):
    """
    Calculate regret after an irrigation decision.

    action_taken: 0 or 1 (what the system decided)
    actual_outcome: 0 or 1 (what SHOULD have been done)
        - derived later from yield / stress / expert label
    data: dict with farm_data.csv fields

    Returns:
        regret score (float, >= 0)
    """

    crop = data["crop"]
    soil_moisture = data["soil_moisture_pct"]
    rainfall = data["rainfall_mm"]
    disease_risk = data["disease_risk"]

    # If decision was correct → zero regret
    if action_taken == actual_outcome:
        return 0.0

    regret = 1.0  # base regret

    # ---------------- CONTEXTUAL WEIGHTING ----------------

    # Missed irrigation during low moisture → high regret
    if action_taken == 0 and soil_moisture < 40:
        regret += 1.5

    # Unnecessary irrigation during high moisture → high regret
    if action_taken == 1 and soil_moisture > 70:
        regret += 1.5

    # Rainfall makes unnecessary irrigation worse
    if action_taken == 1 and rainfall >= 80:
        regret += 2.0

    # Crop sensitivity adjustment
    if crop == "pulses":
        regret *= 1.3  # pulses are fragile

    if crop == "rice":
        regret *= 0.7  # rice tolerates water

    # Disease risk: irrigation during high disease risk is worse
    if disease_risk == "high" and action_taken == 1:
        regret += 1.0

    return float(regret)
