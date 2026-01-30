def build_yield_features(journey):
    """
    Extract yield-relevant indicators from crop journey data
    stored in Supabase (flat schema).

    journey: list of dicts (rows from crop_trace_log)
    """

    irrigation_count = 0
    stress_events = 0
    disease_events = 0

    for stage in journey:
        # ----------------------------------
        # Irrigation events
        # ----------------------------------
        if stage.get("irrigation_decision") == 1:
            irrigation_count += 1

        # ----------------------------------
        # Water stress detection
        # ----------------------------------
        soil_moisture = stage.get("soil_moisture_pct")
        if soil_moisture is not None and soil_moisture < 35:
            stress_events += 1

        # ----------------------------------
        # Disease pressure
        # ----------------------------------
        if stage.get("disease_risk") == "high":
            disease_events += 1

    return {
        "irrigation_count": irrigation_count,
        "stress_events": stress_events,
        "disease_events": disease_events
    }
