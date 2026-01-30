from core.yield_baseline import BASELINE_YIELD
from core.yield_feature_engine import build_yield_features

def predict_yield(crop, journey):
    baseline = BASELINE_YIELD[crop]
    features = build_yield_features(journey)

    # Start from mid baseline
    expected_yield = (baseline["min"] + baseline["max"]) / 2

    # Positive impact
    expected_yield += features["irrigation_count"] * 0.1

    # Negative impact
    expected_yield -= features["stress_events"] * 0.15
    expected_yield -= features["disease_events"] * 0.2

    # Clamp yield
    expected_yield = max(baseline["min"], min(expected_yield, baseline["max"]))

    confidence = "high"
    if features["stress_events"] > 2 or features["disease_events"] > 1:
        confidence = "medium"
    if features["stress_events"] > 4:
        confidence = "low"

    return {
        "expected_yield_t_ha": round(expected_yield, 2),
        "confidence": confidence,
        "drivers": features
    }
