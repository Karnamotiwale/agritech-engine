import requests

url = "http://127.0.0.1:5000/api/v1/chat"
headers = {"Content-Type": "application/json"}
data = {"message": "How can farmers improve soil fertility?"}

try:
    response = requests.post(url, json=data)
    print("Status:", response.status_code)
    print("Body:", response.json())
except Exception as e:
    print("Error:", e)
