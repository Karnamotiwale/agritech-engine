from core.supabase_client import supabase

def log_crop_stage(data, decision, irrigation_plan, fertilizer, pest_advice):
    supabase.table("crop_trace_log").insert({
        "crop": data["crop"],
        "growth_stage": data["growth_stage"],
        "soil_moisture_pct": data["soil_moisture_pct"],
        "rainfall_mm": data["rainfall_mm"],
        "temperature_c": data["temperature_c"],
        "humidity_pct": data["humidity_pct"],
        "irrigation_decision": decision,
        "irrigation_plan": irrigation_plan,
        "fertilizer_advice": fertilizer,
        "pest_disease_advisory": pest_advice
    }).execute()
