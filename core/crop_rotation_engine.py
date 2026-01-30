def recommend_next_crop(crop, crop_journey):
    """
    Recommend next crop after harvest based on:
    - Previous crop
    - Soil nutrient stress
    - Pest & disease history
    """

    # -------------------------------
    # Base rotation rules (agronomy)
    # -------------------------------
    rotation_rules = {
        "rice": {
            "recommended": ["pulses", "wheat"],
            "avoid": ["rice"],
            "reason": "Rice depletes nitrogen and encourages waterborne diseases"
        },
        "wheat": {
            "recommended": ["pulses", "maize"],
            "avoid": ["wheat"],
            "reason": "Continuous wheat increases soil fatigue and rust risk"
        },
        "maize": {
            "recommended": ["pulses", "wheat"],
            "avoid": ["maize"],
            "reason": "Maize benefits from nitrogen-fixing legumes"
        },
        "pulses": {
            "recommended": ["wheat", "maize", "rice"],
            "avoid": [],
            "reason": "Pulses improve soil nitrogen"
        },
        "sugarcane": {
            "recommended": ["pulses"],
            "avoid": ["sugarcane"],
            "reason": "Sugarcane heavily depletes soil nutrients"
        }
    }

    base = rotation_rules.get(crop, {
        "recommended": [],
        "avoid": [],
        "reason": "No specific rule available"
    })

    # -------------------------------
    # Analyze crop journey signals
    # -------------------------------
    disease_events = 0
    water_stress = 0

    for stage in crop_journey:
        if stage.get("disease_risk") == "high":
            disease_events += 1
        if stage.get("soil_moisture_pct", 0) < 40:
            water_stress += 1

    adjustments = []

    if disease_events > 2:
        adjustments.append("Avoid same crop due to disease carryover")

    if water_stress > 2:
        adjustments.append("Prefer low-water-demand crops")

    # -------------------------------
    # Final Recommendation
    # -------------------------------
    return {
        "previous_crop": crop,
        "recommended_next_crops": base["recommended"],
        "avoid_crops": base["avoid"],
        "agronomic_reason": base["reason"],
        "observed_issues": {
            "disease_events": disease_events,
            "water_stress_events": water_stress
        },
        "additional_guidance": adjustments
    }
