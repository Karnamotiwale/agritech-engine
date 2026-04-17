from flask import Blueprint, request, jsonify  # type: ignore

rotation_bp = Blueprint('crop_rotation', __name__)

@rotation_bp.route('/api/v1/crops/rotation', methods=['POST'])
def crop_rotation():
    """
    Suggest Next Crop for Rotation
    """
    data = request.json or {}
    previous_crop = str(data.get("previousCrop", "unknown")).lower().strip()
    
    # Map for Crop Rotation Logic
    rotation_map = {
        "rice": {
            "recommendedCrop": "Soybean",
            "reason": "Restores Nitrogen levels exhausted by Rice cultivation.",
            "benefits": ["Natural Nitrogen Fixation", "Market Demand", "Pest Cycle Break"]
        },
        "wheat": {
            "recommendedCrop": "Pulse Crop (e.g., Lentils, Chickpeas)",
            "reason": "Replenishes soil nutrients lost during intensive Wheat farming.",
            "benefits": ["Symbiotic Nitrogen Fixation", "Disease Break", "Water Efficiency"]
        },
        "cotton": {
            "recommendedCrop": "Legumes",
            "reason": "Improves organic matter and interrupts deep-rooted pest life cycles.",
            "benefits": ["Breaks Pest Cycles", "Adds Organic Matter", "Alternative Income"]
        },
        "maize": {
            "recommendedCrop": "Groundnut",
            "reason": "Leguminous groundnut fixes nitrogen and improves soil structure after Maize.",
            "benefits": ["Soil Structure Improvement", "Nutrient Balancing"]
        }
    }
    
    # Default fallback if unknown crop
    result = rotation_map.get(previous_crop, {
        "recommendedCrop": "Cover Crop (e.g., Clover, Alfalfa)",
        "reason": "General soil recovery and erosion prevention.",
        "benefits": ["Weed Suppression", "Soil Health", "Moisture Retention"]
    })
    
    try:
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "An internal error occurred"}), 500
