import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_weather(lat, lon):
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not OPENWEATHER_API_KEY:
        print("Warning: OPENWEATHER_API_KEY not set")
        return {"error": "API key missing"}
        
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url)
        return response.json()
    except Exception as e:
        print(f"Warning: Failed to fetch weather data: {e}")
        return {"error": "Failed to fetch weather data"}
