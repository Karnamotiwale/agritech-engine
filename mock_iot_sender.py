import time
import random
import requests
from datetime import datetime, timedelta

API_URL = "http://127.0.0.1:5000/decide"
ALLOWED_CROPS = ["rice", "wheat", "maize", "sugarcane", "pulses"]

def generate_sensor_data(crop):
    # Simulated 10-minute status update
    return {
        "crop": crop,
        "growth_stage": "Tillering", # Simplified for generic sender
        "soil_moisture_pct": random.randint(35, 55),
        "rainfall_mm": random.choice([0, 0, 0, 5, 20]),
        "temperature_c": random.randint(22, 32),
        "humidity_pct": random.randint(60, 85),
        "nitrogen_kg_ha": random.randint(80, 120),
        "phosphorus_kg_ha": random.randint(40, 60),
        "potassium_kg_ha": random.randint(30, 50),
        "disease_risk_score": random.randint(0, 40),
        "pest_risk_score": random.randint(0, 40),
        "irrigation_applied_mm": random.choice([0, 10, 20])
    }

print("🚀 Starting Agri-Tech Scheduler...")
print(f"⏱ 10-Minute Cycle: Active for {', '.join(ALLOWED_CROPS)}")
print("⏰ Daily Cycle: Active for Yield & learning updates")

last_daily_run = datetime.now() - timedelta(days=1)

while True:
    now = datetime.now()
    
    # 10-Minute Cycle Logic
    for crop in ALLOWED_CROPS:
        data = generate_sensor_data(crop)
        print(f"📡 [10m Cycle] Sending data for {crop}...")
        try:
            requests.post(API_URL, json=data)
        except Exception as e:
            print(f"❌ Connection error for {crop}: {e}")

    # Daily Cycle Logic (Simulated once every hour for the demo, or once per 24h)
    if (now - last_daily_run).total_seconds() > 3600: # Simulated daily every hour for demo
        print("⏰ [Daily Cycle] Recalculating farm-wide yield trends & RL rewards...")
        for crop in ALLOWED_CROPS:
            try:
                requests.post("http://127.0.0.1:5000/yield/predict", json={"crop": crop})
            except: pass
        last_daily_run = now

    print(f"💤 Cycle complete. Waiting 10 minutes... (Next @ {(now + timedelta(minutes=10)).strftime('%H:%M:%S')})")
    time.sleep(600) # Full 10-minute requirement
