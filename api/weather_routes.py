from flask import Blueprint, request, jsonify
from api.weather_service import get_weather

weather_bp = Blueprint("weather", __name__)

@weather_bp.route("/api/v1/weather", methods=["GET"])
def weather():
    lat = request.args.get("lat")  
    lon = request.args.get("lon")

    data = get_weather(lat, lon)

    return jsonify(data)
