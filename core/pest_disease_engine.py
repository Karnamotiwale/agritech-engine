def generate_pest_disease_advisory(data):
    """
    Rule-based pest & disease advisory engine (non-image).
    """

    crop = data.get("crop")
    disease_risk = data.get("disease_risk")
    pest_risk = data.get("pest_risk")
    stage = data.get("growth_stage")

    advisories = []

    # ---------------- DISEASE ADVISORY ----------------
    if disease_risk == "high":
        if crop == "wheat":
            advisories.append(
                "High disease risk detected. Monitor for rust and avoid excess nitrogen."
            )

        if crop == "rice":
            advisories.append(
                "High disease risk detected. Maintain proper water management to reduce fungal spread."
            )

        if crop == "maize":
            advisories.append(
                "High disease risk detected. Inspect leaves for blight symptoms."
            )

        if crop == "sugarcane":
            advisories.append(
                "High disease risk detected. Check for red rot or smut signs."
            )

        if crop == "pulses":
            advisories.append(
                "High disease risk detected. Monitor for wilt or blight."
            )

    elif disease_risk == "medium":
        advisories.append(
            "Moderate disease risk. Regular field scouting is recommended."
        )

    else:
        advisories.append(
            "Disease risk is low. No immediate disease control required."
        )

    # ---------------- PEST ADVISORY ----------------
    if pest_risk == "high":
        if crop == "wheat":
            advisories.append(
                "High pest risk detected. Monitor for aphids and armyworms."
            )

        if crop == "rice":
            advisories.append(
                "High pest risk detected. Watch for stem borer and planthopper activity."
            )

        if crop == "maize":
            advisories.append(
                "High pest risk detected. Inspect crop for fall armyworm damage."
            )
        
        if crop == "sugarcane":
            advisories.append(
                "High pest risk detected. Monitor for pyrilla or borers."
            )

        if crop == "pulses":
            advisories.append(
                "High pest risk detected. Watch for pod borers."
            )

    elif pest_risk == "medium":
        advisories.append(
            "Moderate pest pressure. Continue monitoring crop regularly."
        )

    else:
        advisories.append(
            "Pest risk is low. No immediate pest management required."
        )

    # ---------------- STAGE-SPECIFIC NOTE ----------------
    if stage in ["Flowering", "Tasseling", "Grain filling", "Pod filling"]:
        advisories.append(
            "Critical growth stage. Pest and disease stress can significantly impact yield."
        )

    return {
        "disease_risk": disease_risk,
        "pest_risk": pest_risk,
        "advisories": advisories
    }
