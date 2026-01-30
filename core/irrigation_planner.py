def plan_irrigation(data, final_decision):
    """
    Rule-based irrigation quantity & scheduling planner.
    """

    crop = data.get("crop")
    stage = data.get("growth_stage")
    soil_moisture = data.get("soil_moisture_pct")

    # If irrigation not recommended
    if final_decision == 0:
        return {
            "apply": False,
            "message": "Irrigation not required at this time"
        }

    water_mm = 0
    next_days = 0
    reason = ""

    # ---------------- WHEAT ----------------
    if crop == "wheat":
        if soil_moisture < 40:
            water_mm = 40
            next_days = 6
            reason = "Low soil moisture during critical wheat growth stage"
        else:
            water_mm = 25
            next_days = 8
            reason = "Moderate moisture, maintenance irrigation"

    # ---------------- RICE ----------------
    if crop == "rice":
        if stage in ["Transplanting", "Tillering"]:
            water_mm = 50
            next_days = 4
            reason = "Rice requires standing water during early stages"
        else:
            water_mm = 30
            next_days = 6
            reason = "Maintenance irrigation for rice"

    # ---------------- MAIZE ----------------
    if crop == "maize":
        if stage in ["Tasseling", "Grain filling"]:
            water_mm = 45
            next_days = 5
            reason = "High water demand during tasseling and grain filling"
        else:
            water_mm = 30
            next_days = 7
            reason = "Regular irrigation for maize"

    # ---------------- PULSES ----------------
    if crop == "pulses":
        water_mm = 20
        next_days = 10
        reason = "Pulses require light and infrequent irrigation"

    # ---------------- SUGARCANE ----------------
    if crop == "sugarcane":
        water_mm = 60
        next_days = 7
        reason = "Sugarcane has high water demand"

    return {
        "apply": True,
        "water_mm": water_mm,
        "next_irrigation_days": next_days,
        "reason": reason
    }
