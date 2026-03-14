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
    print("=" * 50)
    print("  KisaanSaathi Backend")
    print("  http://127.0.0.1:5000")
    print("  Swagger UI: http://127.0.0.1:5000/apidocs")
    print("=" * 50)
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=True
    )
