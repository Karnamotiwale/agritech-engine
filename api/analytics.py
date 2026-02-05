
from flask import Blueprint, jsonify, request
from core.supabase_client import supabase
from core.ai_engine.analytics_predictor import AnalyticsPredictor
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__)
predictor = AnalyticsPredictor()

@analytics_bp.route('/overview', methods=['GET'])
def get_overview():
    """
    Get real-time analytics overview (trends, current values).
    """
    try:
        # Fetch last 100 readings (approx 24h if 15m interval)
        response = supabase.table('sensor_logs').select('*').order('created_at', desc=True).limit(100).execute()
        data = response.data
        
        analysis = predictor.analyze_trends(data)
        
        # Add metadata
        analysis['timestamp'] = datetime.now().isoformat()
        analysis['source'] = 'live_sensor_network' if data else 'simulation_fallback'
        
        return jsonify(analysis)
    except Exception as e:
        print(f"Analytics Error: {e}")
        return jsonify({
            "summary": {},
            "error": str(e),
            "status": "error"
        })

@analytics_bp.route('/range-forecast', methods=['GET'])
def get_forecast():
    """
    Get 7-day forecast for yield/conditions.
    """
    try:
        days = int(request.args.get('days', 7))
        response = supabase.table('sensor_logs').select('*').order('created_at', desc=True).limit(500).execute()
        data = response.data
        
        forecast = predictor.predict_short_term(data, days=days)
        return jsonify({
            "forecast": forecast,
            "horizon_days": days
        })
    except Exception as e:
        print(f"Forecast Error: {e}")
        return jsonify({
            "forecast": [],
            "status": "error",
            "error": str(e)
        })

@analytics_bp.route('/crop-health', methods=['GET'])
def get_crop_health():
    """
    Get aggregated health scores for active crops.
    """
    try:
        # Get active crops
        crops_res = supabase.table('crops').select('*').eq('status', 'active').execute()
        crops = crops_res.data
        
        health_reports = []
        
        # In a real app, we'd do a join or optimized query. 
        # For now, we fetch sensor logs globally or per crop if linked.
        # Assuming global sensors for demo.
        sensor_res = supabase.table('sensor_logs').select('*').limit(50).execute()
        
        for crop in crops:
            score = predictor.calculate_health_score(crop, sensor_res.data)
            health_reports.append({
                "crop_id": crop.get('id'),
                "name": crop.get('name'),
                "health_score": score,
                "status": "Good" if score > 75 else "Attention" if score > 50 else "Critical"
            })
            
        return jsonify({"crops": health_reports})
        
    except Exception as e:
        print(f"Health Error: {e}")
        return jsonify({"crops": [], "error": str(e)})

