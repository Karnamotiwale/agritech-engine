from core.supabase_client import supabase
from core.crop_constants import safe_value

def log_crop_stage(data, decision, irrigation_plan, fertilizer, pest_advice):
    supabase.table("crop_trace_log").insert({
        "crop": data.get("crop"),
        "growth_stage": data.get("growth_stage", "Unknown"),
        "soil_moisture_pct": safe_value(data.get("soil_moisture_pct")),
        "rainfall_mm": safe_value(data.get("rainfall_mm")),
        "temperature_c": safe_value(data.get("temperature_c")),
        "humidity_pct": safe_value(data.get("humidity_pct")),
        "nitrogen_kg_ha": safe_value(data.get("nitrogen_kg_ha")),
        "phosphorus_kg_ha": safe_value(data.get("phosphorus_kg_ha")),
        "potassium_kg_ha": safe_value(data.get("potassium_kg_ha")),
        "disease_risk_score": safe_value(data.get("disease_risk_score")),
        "pest_risk_score": safe_value(data.get("pest_risk_score")),
        "irrigation_applied_mm": safe_value(data.get("irrigation_applied_mm")),
        "irrigation_decision": decision,
        "irrigation_plan": irrigation_plan,
        "fertilizer_advice": fertilizer,
        "pest_disease_advisory": pest_advice
    }).execute()
