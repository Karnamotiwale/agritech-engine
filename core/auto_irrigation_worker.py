import time
import logging
from core.supabase_client import supabase
from core.decision_engine import run_decision_engine

def run_loop():
    """
    Background worker loop for periodic auto-irrigation analysis.
    Loops every 60 seconds (1 minute).
    """
    while True:
        try:
            # Fetch latest reading from recent sensors
            sensors = (
                supabase.table("sensor_readings")
                .select("*")
                .order("created_at", desc=True)
                .limit(10)
                .execute()
            )

            if sensors and sensors.data:
                for s in sensors.data:
                    try:
                        decision = run_decision_engine(s)

                        if decision and decision.get("action") == "IRRIGATE":
                            # Perform the action log
                            action_payload = {
                                "farm_id": s.get("device_id"), # device_id in sensor_readings
                                "crop_id": s.get("crop_id"), 
                                "action": "IRRIGATE",
                                "duration": decision.get("duration", 10)
                            }
                            
                            # Note: In production, there should ideally be a check
                            # here to ensure action is not continuously spammed
                            # if the sensor hasn't updated its state quickly enough.
                            supabase.table("irrigation_actions").insert(action_payload).execute()
                            logging.info(f"Auto Irrigation Worker toggled IRRIGATE for Farm: {s.get('device_id')}")
                    except Exception as inner_e:
                        logging.error(f"Error processing sensor {s.get('device_id')}: {inner_e}")
            
        except Exception as e:
            logging.error(f"Error inside auto irrigation loop: {e}")

        # Sleep for 1 minute before resuming checking
        time.sleep(60)
