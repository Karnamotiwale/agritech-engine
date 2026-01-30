def generate_explanation(data, ml_prediction, decision):
    """
    Generate human-readable explanations and advisories.

    data: dict with farm_data.csv fields
    ml_prediction: ML model's raw prediction (0 or 1)
    decision: final decision after rules/policy/RL (0 or 1)

    Returns:
        dict with explanations and advisories
    """

    explanations = []
    advisories = []

    crop = data["crop"]
    soil_moisture = data["soil_moisture_pct"]
    rainfall = data["rainfall_mm"]
    temperature = data["temperature_c"]
    disease_risk = data["disease_risk"]
    pest_risk = data["pest_risk"]

    nitrogen = data["nitrogen_kg_ha"]
    phosphorus = data["phosphorus_kg_ha"]
    potassium = data["potassium_kg_ha"]

    # ---------------- IRRIGATION EXPLANATION ----------------

    if decision == 1:
        explanations.append(
            f"Irrigation recommended due to low soil moisture ({soil_moisture}%)."
        )
    else:
        explanations.append(
            "Irrigation not recommended based on current field conditions."
        )

    if rainfall >= 80:
        explanations.append(
            "Recent rainfall is sufficient to meet crop water needs."
        )

    # ---------------- NPK ADVISORY (NO DOSAGE) ----------------

    if nitrogen < 50:
        advisories.append(
            "Nitrogen levels appear low; consider nitrogen supplementation as per local guidelines."
        )

    if phosphorus < 40:
        advisories.append(
            "Phosphorus levels may be insufficient; soil test-based correction is advised."
        )

    if potassium < 40:
        advisories.append(
            "Potassium deficiency suspected; consult agronomy recommendations."
        )

    # ---------------- PEST & DISEASE ADVISORY ----------------

    if disease_risk == "high":
        advisories.append(
            "High disease risk detected; avoid excess irrigation and monitor crop health closely."
        )

    if pest_risk == "high":
        advisories.append(
            "High pest pressure detected; field scouting and integrated pest management are recommended."
        )

    # ---------------- WEATHER CONTEXT ----------------

    if temperature > 35:
        advisories.append(
            "High temperature stress possible; ensure timely irrigation and mulching where applicable."
        )

    # ---------------- CROP-SPECIFIC NOTES ----------------

    if crop == "pulses" and soil_moisture > 60:
        advisories.append(
            "Pulses are sensitive to waterlogging; ensure proper drainage."
        )

    if crop == "rice":
        advisories.append(
            "Rice tolerates standing water; follow AWD or flood irrigation practices as suitable."
        )

    return {
        "explanations": explanations,
        "advisories": advisories
    }

