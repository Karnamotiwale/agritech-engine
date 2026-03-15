"""
KisaanSaathi Alert Background Worker
=======================================
Polls the latest sensor data every 90 seconds,
runs threshold checks and Gemini AI alert generation,
and stores results to the smart_alerts table.
"""
import time
import logging
from core.supabase_client import supabase
from core.alert_engine import analyze_and_generate_alerts
import uuid
from datetime import datetime, timezone


def run_alert_loop():
    """
    Background loop — runs every 90 seconds.
    Checks all latest sensor readings and generates AI alerts.
    """
    logging.info("🔔 Smart Alert Worker started.")
    while True:
        try:
            # Get the most recent sensor reading per farm (last 10)
            res = (
                supabase.table("sensor_data")
                .select("*")
                .order("created_at", desc=True)
                .limit(10)
                .execute()
            )

            if res and res.data:
                seen_farms = set()
                for sensor in res.data:
                    farm_id = sensor.get("farm_id", "default")
                    # Only process one reading per farm per cycle
                    if farm_id in seen_farms:
                        continue
                    seen_farms.add(farm_id)

                    alerts = analyze_and_generate_alerts(sensor)

                    if alerts:
                        rows = [
                            {
                                "id": str(uuid.uuid4()),
                                "farm_id": farm_id,
                                "alert_type": a["type"],
                                "title": a["title"],
                                "severity": a["severity"],
                                "message": a["message"],
                                "icon": a.get("icon", "⚠️"),
                                "created_at": datetime.now(timezone.utc).isoformat(),
                            }
                            for a in alerts
                        ]
                        try:
                            supabase.table("smart_alerts").insert(rows).execute()
                            logging.info(f"🔔 Stored {len(rows)} alert(s) for farm: {farm_id}")
                        except Exception as db_err:
                            logging.warning(f"Could not store alerts: {db_err}")

        except Exception as e:
            logging.error(f"Alert worker error: {e}")

        # Sleep 90 seconds before re-checking
        time.sleep(90)
