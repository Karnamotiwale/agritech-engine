import requests
try:
    response = requests.get("http://127.0.0.1:5000/ai/status")
    print(response.status_code)
    print(response.text)
except Exception as e:
    print(f"Error: {e}")
