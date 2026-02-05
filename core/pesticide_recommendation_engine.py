"""
Pesticide Recommendation Engine

Intelligently recommends pesticides based on:
1. Crop type
2. Detected disease or pest
3. Environmental sensor data (humidity, temperature, soil moisture)
4. Crop growth stage

Decision Logic:
- If disease detected → curative pesticide
- If high risk environmental conditions → preventive pesticide
- Otherwise → no pesticide needed
"""

from typing import Dict, Optional, Any


# Pesticide database - In production, this would come from Supabase
PESTICIDE_DATABASE = {
    "rice": {
        "leaf_blast": {
            "pesticide_name": "Tricyclazole",
            "type": "fungicide",
            "category": "curative",
            "dosage": "0.6 g/L",
            "spray_interval_days": 7,
            "safety_notes": "Wear protective gear. Do not spray during flowering.",
            "carbon_impact_score": 12.5
        },
        "stem_borer": {
            "pesticide_name": "Cartap Hydrochloride",
            "type": "insecticide",
            "category": "curative",
            "dosage": "1.0 g/L",
            "spray_interval_days": 10,
            "safety_notes": "Apply during early morning or evening.",
            "carbon_impact_score": 15.0
        },
        "brown_planthopper": {
            "pesticide_name": "Imidacloprid",
            "type": "insecticide",
            "category": "curative",
            "dosage": "0.5 ml/L",
            "spray_interval_days": 14,
            "safety_notes": "Avoid spray drift to water bodies.",
            "carbon_impact_score": 18.0
        },
        "preventive_fungal": {
            "pesticide_name": "Copper Oxychloride",
            "type": "fungicide",
            "category": "preventive",
            "dosage": "2.5 g/L",
            "spray_interval_days": 10,
            "safety_notes": "Use as preventive measure during humid conditions.",
            "carbon_impact_score": 8.0
        }
    },
    "wheat": {
        "rust": {
            "pesticide_name": "Propiconazole",
            "type": "fungicide",
            "category": "curative",
            "dosage": "1.0 ml/L",
            "spray_interval_days": 10,
            "safety_notes": "Apply at first sign of rust pustules.",
            "carbon_impact_score": 14.0
        },
        "aphids": {
            "pesticide_name": "Imidacloprid",
            "type": "insecticide",
            "category": "curative",
            "dosage": "0.4 ml/L",
            "spray_interval_days": 14,
            "safety_notes": "Monitor aphid population before spraying.",
            "carbon_impact_score": 16.0
        },
        "armyworm": {
            "pesticide_name": "Chlorantraniliprole",
            "type": "insecticide",
            "category": "curative",
            "dosage": "0.3 ml/L",
            "spray_interval_days": 12,
            "safety_notes": "Apply when larvae are small for best results.",
            "carbon_impact_score": 20.0
        },
        "preventive_fungal": {
            "pesticide_name": "Mancozeb",
            "type": "fungicide",
            "category": "preventive",
            "dosage": "2.0 g/L",
            "spray_interval_days": 14,
            "safety_notes": "Use during cool, wet conditions.",
            "carbon_impact_score": 10.0
        }
    },
    "maize": {
        "fall_armyworm": {
            "pesticide_name": "Chlorantraniliprole",
            "type": "insecticide",
            "category": "curative",
            "dosage": "0.4 ml/L",
            "spray_interval_days": 10,
            "safety_notes": "Target whorl and ear zones.",
            "carbon_impact_score": 22.0
        },
        "blight": {
            "pesticide_name": "Mancozeb",
            "type": "fungicide",
            "category": "curative",
            "dosage": "2.5 g/L",
            "spray_interval_days": 7,
            "safety_notes": "Apply at first sign of leaf spots.",
            "carbon_impact_score": 12.0
        },
        "stem_borer": {
            "pesticide_name": "Fipronil",
            "type": "insecticide",
            "category": "curative",
            "dosage": "1.5 ml/L",
            "spray_interval_days": 14,
            "safety_notes": "Apply during vegetative stage.",
            "carbon_impact_score": 18.0
        },
        "preventive_fungal": {
            "pesticide_name": "Azoxystrobin",
            "type": "fungicide",
            "category": "preventive",
            "dosage": "1.0 ml/L",
            "spray_interval_days": 14,
            "safety_notes": "Use preventively during rainy season.",
            "carbon_impact_score": 9.0
        }
    },
    "sugarcane": {
        "red_rot": {
            "pesticide_name": "Carbendazim",
            "type": "fungicide",
            "category": "curative",
            "dosage": "1.0 g/L",
            "spray_interval_days": 15,
            "safety_notes": "Treat setts before planting.",
            "carbon_impact_score": 14.5
        },
        "pyrilla": {
            "pesticide_name": "Thiamethoxam",
            "type": "insecticide",
            "category": "curative",
            "dosage": "0.5 ml/L",
            "spray_interval_days": 14,
            "safety_notes": "Monitor nymph population.",
            "carbon_impact_score": 17.0
        },
        "borer": {
            "pesticide_name": "Fipronil",
            "type": "insecticide",
            "category": "curative",
            "dosage": "2.0 ml/L",
            "spray_interval_days": 21,
            "safety_notes": "Apply granules in leaf whorl.",
            "carbon_impact_score": 19.0
        },
        "preventive_fungal": {
            "pesticide_name": "Copper Fungicide",
            "type": "fungicide",
            "category": "preventive",
            "dosage": "2.0 g/L",
            "spray_interval_days": 21,
            "safety_notes": "Use during monsoon season.",
            "carbon_impact_score": 7.5
        }
    },
    "pulses": {
        "pod_borer": {
            "pesticide_name": "Emamectin Benzoate",
            "type": "insecticide",
            "category": "curative",
            "dosage": "0.4 g/L",
            "spray_interval_days": 10,
            "safety_notes": "Apply during pod formation stage.",
            "carbon_impact_score": 16.5
        },
        "wilt": {
            "pesticide_name": "Carbendazim",
            "type": "fungicide",
            "category": "curative",
            "dosage": "1.0 g/L",
            "spray_interval_days": 14,
            "safety_notes": "Drench soil around plant base.",
            "carbon_impact_score": 13.0
        },
        "aphids": {
            "pesticide_name": "Dimethoate",
            "type": "insecticide",
            "category": "curative",
            "dosage": "1.5 ml/L",
            "spray_interval_days": 12,
            "safety_notes": "Apply when aphids first appear.",
            "carbon_impact_score": 15.5
        },
        "preventive_fungal": {
            "pesticide_name": "Bio-Fungicide (Trichoderma)",
            "type": "bio-pesticide",
            "category": "preventive",
            "dosage": "5 g/L",
            "spray_interval_days": 14,
            "safety_notes": "Organic alternative with low toxicity.",
            "carbon_impact_score": -5.0  # Negative = carbon reduction
        }
    }
}


def assess_risk_from_environment(humidity: float, temperature: float, crop: str) -> Dict[str, Any]:
    """
    Assess pest/disease risk based on environmental conditions.
    
    Returns:
        dict with risk_level and recommended_action
    """
    risk_level = "low"
    recommendation = None
    
    # High humidity + moderate temperature = Fungal risk
    if humidity > 80 and 20 <= temperature <= 28:
        risk_level = "high"
        recommendation = "preventive_fungal"
    
    # Very high temperature = Pest activity increase
    elif temperature > 35 and crop in ["rice", "wheat"]:
        risk_level = "medium"
        recommendation = None  # Monitor only
    
    # Moderate humidity during flowering = Critical
    elif 60 <= humidity <= 75 and crop in ["pulses", "wheat"]:
        risk_level = "medium"
        recommendation = None
    
    return {
        "risk_level": risk_level,
        "environmental_recommendation": recommendation
    }


def get_pesticide_recommendation(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to generate pesticide recommendation.
    
    Args:
        data: dict containing:
            - crop: str (rice, wheat, maize, sugarcane, pulses)
            - disease: str (optional, detected disease name)
            - pest: str (optional, detected pest name)
            - growth_stage: str (optional)
            - humidity: float (optional)
            - temperature: float (optional)
            - soil_moisture: float (optional)
    
    Returns:
        dict with recommendation details or "no action required"
    """
    crop = data.get("crop", "").lower()
    disease = data.get("disease", "").lower().replace(" ", "_")
    pest = data.get("pest", "").lower().replace(" ", "_")
    growth_stage = data.get("growth_stage", "")
    humidity = data.get("humidity", 0)
    temperature = data.get("temperature", 0)
    
    # Validate crop
    if crop not in PESTICIDE_DATABASE:
        return {
            "status": "error",
            "message": f"Invalid crop. Supported: rice, wheat, maize, sugarcane, pulses"
        }
    
    # PRIORITY 1: Disease detected - recommend curative
    if disease and disease in PESTICIDE_DATABASE[crop]:
        pesticide_info = PESTICIDE_DATABASE[crop][disease]
        return {
            "status": "recommendation",
            "trigger": "disease_detected",
            "disease": disease.replace("_", " ").title(),
            "pesticide": pesticide_info["pesticide_name"],
            "type": pesticide_info["type"],
            "category": pesticide_info["category"],
            "dosage": pesticide_info["dosage"],
            "spray_interval": f"{pesticide_info['spray_interval_days']} days",
            "safety_notes": pesticide_info["safety_notes"],
            "carbon_impact": pesticide_info["carbon_impact_score"],
            "carbon_impact_label": f"+{pesticide_info['carbon_impact_score']}%" if pesticide_info['carbon_impact_score'] > 0 else f"{pesticide_info['carbon_impact_score']}%"
        }
    
    # PRIORITY 2: Pest detected - recommend curative
    if pest and pest in PESTICIDE_DATABASE[crop]:
        pesticide_info = PESTICIDE_DATABASE[crop][pest]
        return {
            "status": "recommendation",
            "trigger": "pest_detected",
            "pest": pest.replace("_", " ").title(),
            "pesticide": pesticide_info["pesticide_name"],
            "type": pesticide_info["type"],
            "category": pesticide_info["category"],
            "dosage": pesticide_info["dosage"],
            "spray_interval": f"{pesticide_info['spray_interval_days']} days",
            "safety_notes": pesticide_info["safety_notes"],
            "carbon_impact": pesticide_info["carbon_impact_score"],
            "carbon_impact_label": f"+{pesticide_info['carbon_impact_score']}%" if pesticide_info['carbon_impact_score'] > 0 else f"{pesticide_info['carbon_impact_score']}%"
        }
    
    # PRIORITY 3: Environmental risk assessment
    if humidity and temperature:
        risk_assessment = assess_risk_from_environment(humidity, temperature, crop)
        
        if risk_assessment["risk_level"] == "high" and risk_assessment["environmental_recommendation"]:
            preventive_key = risk_assessment["environmental_recommendation"]
            if preventive_key in PESTICIDE_DATABASE[crop]:
                pesticide_info = PESTICIDE_DATABASE[crop][preventive_key]
                return {
                    "status": "recommendation",
                    "trigger": "environmental_risk",
                    "risk_level": "high",
                    "reason": f"High humidity ({humidity}%) and temperature ({temperature}°C) create favorable conditions for fungal diseases",
                    "pesticide": pesticide_info["pesticide_name"],
                    "type": pesticide_info["type"],
                    "category": pesticide_info["category"],
                    "dosage": pesticide_info["dosage"],
                    "spray_interval": f"{pesticide_info['spray_interval_days']} days",
                    "safety_notes": pesticide_info["safety_notes"],
                    "carbon_impact": pesticide_info["carbon_impact_score"],
                    "carbon_impact_label": f"+{pesticide_info['carbon_impact_score']}%" if pesticide_info['carbon_impact_score'] > 0 else f"{pesticide_info['carbon_impact_score']}%"
                }
        
        elif risk_assessment["risk_level"] == "medium":
            return {
                "status": "monitor",
                "trigger": "moderate_risk",
                "message": "Environmental conditions indicate moderate risk. Continue monitoring crop regularly.",
                "humidity": humidity,
                "temperature": temperature
            }
    
    # PRIORITY 4: No action needed
    return {
        "status": "no_action",
        "message": "No immediate pesticide treatment required. Conditions are favorable.",
        "recommendation": "Continue regular field monitoring"
    }


def get_stage_specific_advisory(crop: str, growth_stage: str) -> Optional[str]:
    """
    Get stage-specific pest/disease advisory.
    
    Args:
        crop: crop type
        growth_stage: current growth stage
    
    Returns:
        Advisory message or None
    """
    critical_stages = {
        "rice": ["Flowering", "Grain filling"],
        "wheat": ["Flowering", "Grain filling", "Heading"],
        "maize": ["Tasseling", "Silking", "Grain filling"],
        "sugarcane": ["Tillering", "Grand growth"],
        "pulses": ["Flowering", "Pod filling", "Pod development"]
    }
    
    if crop in critical_stages and growth_stage in critical_stages[crop]:
        return f"⚠️ Critical stage: {growth_stage}. Pest and disease stress can significantly impact yield. Enhanced monitoring recommended."
    
    return None
