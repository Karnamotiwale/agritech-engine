def predict_yield(data):
    crop = data.get("crop", "rice")
    area = data.get("area", 1)

    base_yield = {
        "rice": 5,
        "wheat": 4,
        "maize": 6,
        "cotton": 2,
        "soybean": 3
    }

    base = base_yield.get(crop.lower(), 3)

    # basic factors
    soil_factor = 0.9
    weather_factor = 0.95
    irrigation_factor = 0.92
    fertilizer_factor = 0.94

    predicted = base * soil_factor * weather_factor * irrigation_factor * fertilizer_factor

    return {
        "yield": round(predicted, 2),
        "unit": "tons/hectare",
        "confidence": 88,
        "harvest_window": "Oct 15 - Oct 25"
    }
