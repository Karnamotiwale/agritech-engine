import requests
import os
import logging
from core.supabase_client import supabase
from api.local_db_utils import get_all_farms

def get_weather(farm_id):
    """
    Get weather from OpenWeather API for a given location.
    Uses fallback and offline mocks if the API fails.
    """
    WEATHER_API = os.getenv("OPENWEATHER_API_KEY") or os.getenv("WEATHER_API")
    
    lat, lon = 28.6, 77.2
    try:
        if farm_id and farm_id != "default":
            res = supabase.table("farms").select("latitude, longitude").eq("id", farm_id).execute()
            if res.data and len(res.data) > 0:
                lat = float(res.data[0].get("latitude") or 28.6)
                lon = float(res.data[0].get("longitude") or 77.2)
            else:
                for f in get_all_farms():
                    if f.get("id") == farm_id:
                        lat = float(f.get("latitude") or 28.6)
                        lon = float(f.get("longitude") or 77.2)
                        break
    except Exception as e:
        logging.error(f"Error fetching farm coordinates for weather: {e}")
        
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
            "lat": lat,
            "lon": lon,
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
                "rain_probability": float("{:.1f}".format(item.get("pop", 0.2) * 100))
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

