import os
from dotenv import load_dotenv

# Load from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

_supabase_client = None

class SupabaseProxy:
    def _get_client(self):
        global _supabase_client
        if _supabase_client is None:
            url = os.getenv("SUPABASE_URL")
            key = os.getenv("SUPABASE_KEY")
            if not url or not key:
                print("Warning: SUPABASE_URL or SUPABASE_KEY not set")
                return None
            try:
                from supabase import create_client
                _supabase_client = create_client(url, key)
            except Exception as e:
                print(f"Warning: Supabase client initialization failed: {e}")
        return _supabase_client

    def table(self, *args, **kwargs):
        client = self._get_client()
        if client:
            return client.table(*args, **kwargs)
        
        # Safe dummy object to prevent application crash on query
        class DummyTable:
            def select(self, *a, **k): return self
            def eq(self, *a, **k): return self
            def order(self, *a, **k): return self
            def limit(self, *a, **k): return self
            def execute(self):
                class DummyRes: data = []
                return DummyRes()
            def insert(self, *a, **k): return self
            def update(self, *a, **k): return self
            def delete(self, *a, **k): return self
        return DummyTable()

supabase = SupabaseProxy()

