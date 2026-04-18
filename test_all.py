import requests
import uuid
import json
import sys

# Force UTF-8
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://127.0.0.1:5000"

print("=" * 50)
print("TEST 1: Chat Advisory (/api/v1/chat)")
print("=" * 50)
try:
    r = requests.post(f"{BASE}/api/v1/chat", json={"message": "How to improve soil fertility?"}, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"ERROR: {e}")

print()
print("=" * 50)
print("TEST 2: AI Advisory (/api/v1/ai-advisory)")
print("=" * 50)
try:
    r = requests.post(f"{BASE}/api/v1/ai-advisory", json={"message": "Best time to plant wheat?"}, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"ERROR: {e}")

print()
print("=" * 50)
print("TEST 3: Disease Detection (/api/v1/crops/detect-disease)")
print("=" * 50)
try:
    from PIL import Image
    img = Image.new('RGB', (100, 100), color='green')
    fname = f"test_{uuid.uuid4().hex}.jpg"
    img.save(fname)
    with open(fname, "rb") as f:
        r = requests.post(f"{BASE}/api/v1/crops/detect-disease", files={"image": f}, timeout=30)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
    import os
    os.remove(fname)
except Exception as e:
    print(f"ERROR: {e}")

print()
print("=" * 50)
print("TEST 4: Gemini Status")
print("=" * 50)
try:
    r = requests.get(f"{BASE}/api/v1/ai/gemini-status", timeout=10)
    print(f"Status: {r.status_code}")
    print(f"Response: {json.dumps(r.json(), indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"ERROR: {e}")
