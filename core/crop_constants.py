# core/crop_constants.py

ALLOWED_CROPS = ["rice", "wheat", "maize", "sugarcane", "pulses"]

CROP_LIFECYCLES = {
    "rice": [
        {"name": "Nursery", "min_day": 0, "max_day": 20},
        {"name": "Transplanting", "min_day": 20, "max_day": 30},
        {"name": "Tillering", "min_day": 30, "max_day": 60},
        {"name": "Flowering", "min_day": 60, "max_day": 90},
        {"name": "Maturity", "min_day": 90, "max_day": 120}
    ],
    "wheat": [
        {"name": "Germination", "min_day": 0, "max_day": 10},
        {"name": "Tillering", "min_day": 10, "max_day": 35},
        {"name": "CRI", "min_day": 35, "max_day": 45},
        {"name": "Flowering", "min_day": 60, "max_day": 80},
        {"name": "Maturity", "min_day": 100, "max_day": 120}
    ],
    "maize": [
        {"name": "Emergence", "min_day": 0, "max_day": 10},
        {"name": "Vegetative", "min_day": 10, "max_day": 40},
        {"name": "Tasseling", "min_day": 40, "max_day": 60},
        {"name": "Grain filling", "min_day": 60, "max_day": 90},
        {"name": "Harvest", "min_day": 90, "max_day": 110}
    ],
    "sugarcane": [
        {"name": "Germination", "min_day": 0, "max_day": 30},
        {"name": "Tillering", "min_day": 30, "max_day": 120},
        {"name": "Grand growth", "min_day": 120, "max_day": 270},
        {"name": "Maturity", "min_day": 270, "max_day": 360}
    ],
    "pulses": [
        {"name": "Germination", "min_day": 0, "max_day": 7},
        {"name": "Vegetative", "min_day": 7, "max_day": 30},
        {"name": "Flowering", "min_day": 30, "max_day": 45},
        {"name": "Pod filling", "min_day": 45, "max_day": 65},
        {"name": "Harvest", "min_day": 65, "max_day": 90}
    ]
}

def validate_crop(crop: str):
    """
    Validates if the crop is in the allowed whitelist.
    Raises ValueError if not supported.
    """
    if not crop:
        raise ValueError("Crop name cannot be empty")
    
    crop_lower = crop.lower()
    if crop_lower not in ALLOWED_CROPS:
        raise ValueError(f"Crop '{crop}' is not supported. Allowed: {', '.join(ALLOWED_CROPS)}")
    return crop_lower

def safe_value(value):
    """
    Default missing or non-applicable values to 0.
    """
    if value is None:
        return 0
    try:
        # Check if it's a number
        return float(value)
    except (ValueError, TypeError):
        return 0
