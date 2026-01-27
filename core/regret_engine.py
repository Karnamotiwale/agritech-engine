def analyze_regret(decision, outcome):
    """
    decision: 0 or 1 (final decision)
    outcome: string describing actual result
    """

    regret = False
    reason = "Decision was appropriate"

    # If irrigated but rain happened → regret
    if decision == 1 and outcome == "rain":
        regret = True
        reason = "Irrigation was unnecessary due to rain"

    # If did not irrigate and crop stress increased → regret
    if decision == 0 and outcome == "crop_stress":
        regret = True
        reason = "Crop stress increased due to no irrigation"

    return {
        "regret": regret,
        "reason": reason
    }
