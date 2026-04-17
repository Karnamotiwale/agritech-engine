"""
KisaanSaathi Backend — Startup Script
Run from the agritech-engine directory:
  python run.py
"""
import sys
import os

# Make sure the project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load .env from this directory
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

# Import and run the Flask app
from api.app import app

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug_mode = os.environ.get("FLASK_ENV") == "development"
    base_url = os.environ.get("BASE_URL", f"http://127.0.0.1:{port}")
    print("=" * 50)
    print("  KisaanSaathi Backend")
    print(f"  {base_url}")
    print(f"  Swagger UI: {base_url}/apidocs")
    print("=" * 50)
    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug_mode,
        use_reloader=debug_mode
    )
