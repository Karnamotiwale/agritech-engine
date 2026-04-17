import requests
import json
import time
import os

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:5000")

def test_system_cycle():
    print("--- STARTING END TO END SYSTEM CYCLE TEST ---")
    
    # Payload
    payload = {
        "farm_id": "testfarm",
        "crop_id": "testcrop",
        "moisture": 30,
        "nitrogen": 12,
        "phosphorus": 8,
        "potassium": 10,
        "temperature": 29,
        "humidity": 70
    }
    
    print("\n[1] Pushing Sensor Data via POST /sensor-data")
    try:
        r = requests.post(f"{BASE_URL}/sensor-data", json=payload)
        print(f"Status Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Failed to push sensor data: {e}")

    print("\n[2] Fetching Live Dashboard via GET /farm/dashboard/testfarm")
    try:
        r = requests.get(f"{BASE_URL}/farm/dashboard/testfarm")
        print(f"Status Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Failed to fetch dashboard: {e}")

    print("\n[3] Opening Valve manually via POST /valve/open")
    try:
        r = requests.post(f"{BASE_URL}/valve/open", json={"farm_id": "testfarm", "crop_id": "testcrop", "duration": 5})
        print(f"Status Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Failed to open valve: {e}")

    print("\n[4] Stopping Valve manually via POST /valve/stop")
    try:
        r = requests.post(f"{BASE_URL}/valve/stop", json={"farm_id": "testfarm", "crop_id": "testcrop"})
        print(f"Status Code: {r.status_code}")
        print(f"Response: {json.dumps(r.json(), indent=2)}")
    except Exception as e:
        print(f"Failed to stop valve: {e}")

    print("\n--- END OF TEST ---")

if __name__ == "__main__":
    test_system_cycle()
