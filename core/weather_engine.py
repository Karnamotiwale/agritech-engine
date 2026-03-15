import requests
import os
import logging

def get_weather(farm_id):
    """
    Get weather from OpenWeather API for a given location.
    Uses fallback and offline mocks if the API fails.
    """
    WEATHER_API = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API")
    
    try:
        if not WEATHER_API:
            # Fallback mock weather if missing API key
            return {
                "temperature": 30,
                "humidity": 65,
                "rain_probability": 20
            }

        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": 28.6,
            "lon": 77.2,
            "appid": WEATHER_API,
            "units": "metric",
            "cnt": 1
        }

        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            item = data.get("list", [{}])[0]
            return {
                "temperature": item.get("main", {}).get("temp", 30),
                "humidity": item.get("main", {}).get("humidity", 65),
                "rain_probability": round(item.get("pop", 0.2) * 100, 1)
            }
        else:
            logging.error(f"Weather API Error: {r.status_code}")
    except Exception as e:
        logging.error(f"Error fetching weather: {e}")
        
    # Return mock data on failure
    return {
        "temperature": 30,
        "humidity": 65,
        "rain_probability": 20
    }

