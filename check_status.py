import requests
import os

try:
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:5000")
    response = requests.get(f"{base_url}/ai/status")
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
