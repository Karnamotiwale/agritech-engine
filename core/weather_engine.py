import requests
import os
import logging

def get_weather(farm_id):
    """
    Get weather from OpenWeather API for a given location.
    Uses fallback and offline mocks if the API fails.
    """
    WEATHER_API = os.getenv("WEATHER_API")
    
    try:
        if not WEATHER_API:
            # Fallback mock weather if missing API key
            return {
                "temperature": 30,
                "humidity": 65,
                "rain_probability": 20
            }

        url = "https://api.openweathermap.org/data/2.5/weather"
        # Example lat/lon for the farm
        params = {
            "lat": 28.6,
            "lon": 77.2,
            "appid": WEATHER_API,
            "units": "metric"
        }

        r = requests.get(url, params=params, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "temperature": data.get("main", {}).get("temp", 30),
                "humidity": data.get("main", {}).get("humidity", 65),
                "rain_probability": 20 # Simulate rain probability 
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
