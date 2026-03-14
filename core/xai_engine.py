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

    crop = data.get("crop", "unknown")
    soil_moisture = float(data.get("soil_moisture_pct") or 50.0)
    rainfall = float(data.get("rainfall_mm") or 0.0)
    temperature = float(data.get("temperature_c") or 25.0)
    disease_risk = data.get("disease_risk", "low")
    pest_risk = data.get("pest_risk", "low")

    nitrogen = float(data.get("nitrogen_kg_ha") or 50.0)
    phosphorus = float(data.get("phosphorus_kg_ha") or 50.0)
    potassium = float(data.get("potassium_kg_ha") or 50.0)

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

