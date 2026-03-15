
import time
import logging
from core.supabase_client import supabase
from core.decision_engine import run_decision_engine
from core.rl_engine import get_state, update_q_table

def run_loop():
    """
    Background worker loop for periodic auto-irrigation analysis.
    Loops every 60 seconds (1 minute).

    Full AI loop:
      Supabase sensor_data
          → run_decision_engine (rule + weather)
          → IRRIGATE action logged
          → RL Q-table updated with reward (+1 irrigate, -0.5 wait)
    """
    logging.info("💧 Auto Irrigation Worker started.")
    while True:
        try:
            # Fetch latest reading from recent sensors
            sensors = (
                supabase.table("sensor_data")
                .select("*")
                .order("created_at", desc=True)
                .limit(10)
                .execute()
            )

            if sensors and sensors.data:
                for s in sensors.data:
                    try:
                        decision = run_decision_engine(s)
                        action = decision.get("action", "WAIT")

                        if action == "IRRIGATE":
                            action_payload = {
                                "farm_id": s.get("farm_id", "default"),
                                "crop_id": s.get("crop_id", "default"),
                                "action": "IRRIGATE",
                                "duration": decision.get("duration", 10)
                            }
                            supabase.table("irrigation_actions").insert(action_payload).execute()
                            logging.info(f"💧 Auto Irrigation toggled IRRIGATE for Farm: {s.get('farm_id')}")

                            # RL Q-table update: reward +1 for irrigating when moisture was low
                            try:
                                rl_data = {
                                    "soil_moisture_pct": float(s.get("soil_moisture") or 40),
                                    "rainfall_mm": 0,
                                    "crop": s.get("crop_type", "wheat"),
                                    "growth_stage": "Vegetative",
                                    "disease_risk": "low",
                                    "pest_risk": "low",
                                }
                                state = get_state(rl_data)
                                update_q_table(state, action=1, reward=1.0)
                            except Exception as rl_err:
                                logging.warning(f"RL update failed (non-critical): {rl_err}")

                        else:
                            # RL Q-table: small reward for waiting when moisture is adequate
                            try:
                                rl_data = {
                                    "soil_moisture_pct": float(s.get("soil_moisture") or 60),
                                    "rainfall_mm": 0,
                                    "crop": s.get("crop_type", "wheat"),
                                    "growth_stage": "Vegetative",
                                    "disease_risk": "low",
                                    "pest_risk": "low",
                                }
                                state = get_state(rl_data)
                                update_q_table(state, action=0, reward=0.3)
                            except Exception as rl_err:
                                logging.warning(f"RL update failed (non-critical): {rl_err}")

                    except Exception as inner_e:
                        logging.error(f"Error processing sensor {s.get('farm_id')}: {inner_e}")
            
        except Exception as e:
            logging.error(f"Error inside auto irrigation loop: {e}")

        # Sleep for 1 minute before resuming checking
        time.sleep(60)
