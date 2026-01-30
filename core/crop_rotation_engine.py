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
            "recommended": ["pulses", "maize"],
            "avoid": ["rice"],
            "reason": "Rice depletes nitrogen; rotating with pulses restores it, maize breaks pest cycle"
        },
        "wheat": {
            "recommended": ["rice", "maize"],
            "avoid": ["wheat"],
            "reason": "Rotating wheat with rice or maize prevents soil fatigue and reduces rust risk"
        },
        "maize": {
            "recommended": ["pulses", "wheat"],
            "avoid": ["maize"],
            "reason": "Maize benefits from nitrogen-fixing legumes like pulses"
        },
        "pulses": {
            "recommended": ["rice", "wheat", "maize"],
            "avoid": [],
            "reason": "Pulses improve soil nitrogen for cereal crops"
        },
        "sugarcane": {
            "recommended": ["pulses"],
            "avoid": ["sugarcane"],
            "reason": "Sugarcane heavily depletes soil; pulse rotation is essential for recovery"
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
