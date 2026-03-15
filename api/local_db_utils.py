import json
import os
import uuid

DB_FILE = os.path.join(os.path.dirname(__file__), 'local_db.json')

def load_db():
    if not os.path.exists(DB_FILE):
        return {"farms": [], "crops": []}
    with open(DB_FILE, 'r') as f:
        try:
            return json.load(f)
        except:
            return {"farms": [], "crops": []}

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_all_farms():
    return load_db().get("farms", [])

def add_local_farm(farm_data):
    db = load_db()
    farm_data["id"] = str(uuid.uuid4())
    db["farms"].append(farm_data)
    save_db(db)
    return farm_data

def get_all_crops(farm_id=None):
    crops = load_db().get("crops", [])
    if farm_id:
        return [c for c in crops if c.get("farm_id") == farm_id]
    return crops

def add_local_crop(crop_data):
    db = load_db()
    crop_data["id"] = str(uuid.uuid4())
    db["crops"].append(crop_data)
    save_db(db)
    return crop_data
