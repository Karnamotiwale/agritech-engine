def is_action_allowed(action, data=None):
    """
    Policy layer: final safety gate.
    action: 0 (do not irrigate) or 1 (irrigate)
    data: dict with farm_data.csv fields
    """

    # If no irrigation requested, always allowed
    if action == 0:
        return True

    # Defensive check
    if data is None:
        return False

    crop = data["crop"]
    soil_moisture = data["soil_moisture_pct"]
    rainfall = data["rainfall_mm"]
    disease_risk = data["disease_risk"]
    pest_risk = data["pest_risk"]

    # ---------------- GLOBAL SAFETY RULES ----------------

    # Rule 1: Heavy rainfall blocks irrigation
    if rainfall >= 80:
        return False

    # Rule 2: High soil moisture blocks irrigation
    if soil_moisture >= 70:
        return False

    # ---------------- CROP-SPECIFIC RULES ----------------

    # Pulses: extremely sensitive to waterlogging
    if crop == "pulses" and soil_moisture > 60:
        return False

    # Rice: allow irrigation even at higher moisture (flooded crop)
    if crop == "rice" and soil_moisture <= 85:
        return True

    # Wheat & maize: moderate tolerance
    if crop in ["wheat", "maize"] and soil_moisture > 65:
        return False

    # Sugarcane: deep-rooted but avoid excess water
    if crop == "sugarcane" and soil_moisture > 80:
        return False

    # ---------------- DISEASE / PEST RULES ----------------

    # High disease risk → avoid irrigation (reduces fungal spread)
    if disease_risk == "high":
        return False

    # Pest risk alone does NOT block irrigation
    # (handled in advisory, not control)

    # ---------------- DEFAULT ----------------

    return True
