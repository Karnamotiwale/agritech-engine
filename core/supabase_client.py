import os
from supabase import create_client
from dotenv import load_dotenv

# Load from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise RuntimeError("Supabase environment variables not set")

supabase = create_client(url, key)
