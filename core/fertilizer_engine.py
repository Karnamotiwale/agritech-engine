def recommend_fertilizer(data):
    """
    Rule-based fertilizer recommendation engine.
    Returns fertilizer advice based on crop, stage, and NPK.
    """

    crop = data.get("crop")
    stage = data.get("growth_stage")

    n = data.get("nitrogen_kg_ha")
    p = data.get("phosphorus_kg_ha")
    k = data.get("potassium_kg_ha")

    recommendation = None
    quantity = None
    reason = None

    # ---------------- WHEAT ----------------
    if crop == "wheat":
        if stage == "cri" and n < 120:
            recommendation = "Nitrogen (Urea)"
            quantity = 25
            reason = "Nitrogen deficiency during CRI stage reduces tillering"

        elif stage == "tillering" and n < 100:
            recommendation = "Nitrogen (Urea)"
            quantity = 20
            reason = "Additional nitrogen supports vegetative growth"

    # ---------------- RICE ----------------
    if crop == "rice":
        if stage in ["tillering", "panicle_initiation"] and n < 100:
            recommendation = "Nitrogen (Urea)"
            quantity = 30
            reason = "Nitrogen is critical during active vegetative growth in rice"

        if p < 40:
            recommendation = "Phosphorus (DAP / SSP)"
            quantity = 20
            reason = "Low phosphorus affects root development"

    # ---------------- MAIZE ----------------
    if crop == "maize":
        if stage == "knee_high" and n < 120:
            recommendation = "Nitrogen (Urea)"
            quantity = 30
            reason = "Maize requires nitrogen during rapid vegetative growth"

        if k < 40:
            recommendation = "Potassium (MOP)"
            quantity = 20
            reason = "Potassium improves drought tolerance and grain filling"

    # ---------------- DEFAULT ----------------
    if recommendation is None:
        return {
            "status": "sufficient",
            "message": "Nutrient levels are adequate at this stage"
        }

    return {
        "status": "apply",
        "fertilizer": recommendation,
        "quantity_kg_ha": quantity,
        "reason": reason
    }
