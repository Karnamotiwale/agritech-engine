import time
from core.supabase_client import supabase

def schedule_irrigation(farm_id, crop_id, duration):
    try:
        action = {
            "device_id": farm_id,
            "task_type": "IRRIGATE",
            "scheduled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }

        # Log to task schedules
        supabase.table("task_schedules").insert(action).execute()

        # Simulate delay depending on irrigation duration
        # In a real environment, this might be handled by an async job queue (e.g. celery)
        time.sleep(duration * 60)

        # Log stop action
        supabase.table("irrigation_actions").insert({
            "device_id": farm_id,
            "action": "STOP"
        }).execute()
        
    except Exception as e:
        print(f"Error scheduling irrigation: {e}")
