import time
import random
import requests

API_URL = "http://127.0.0.1:5000/decide"

def generate_sensor_data():
    return {
        "crop": "wheat",
        "growth_stage": "cri",
        "soil_moisture_pct": random.randint(30, 60),
        "rainfall_mm": random.choice([0, 0, 5, 10]),
        "temperature_c": random.randint(25, 35),
        "humidity_pct": random.randint(50, 80),
        "soil_ph": round(random.uniform(6.5, 7.5), 1),
        "nitrogen_kg_ha": 120,
        "phosphorus_kg_ha": 55,
        "potassium_kg_ha": 45,
        "disease_risk": "low",
        "pest_risk": "low"
    }

while True:
    data = generate_sensor_data()
    print("📡 Sending sensor data:", data)

    try:
        response = requests.post(API_URL, json=data)
        print("🤖 AI Response:", response.json())
    except Exception as e:
        print("❌ Error:", e)

    print("-" * 50)
    time.sleep(10)  # send every 10 seconds