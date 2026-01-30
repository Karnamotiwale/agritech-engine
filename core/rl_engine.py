import random
from core.supabase_client import supabase

TABLE_NAME = "rl_q_table"

# --------------------------------------------------
# ACTION SPACE
# --------------------------------------------------
ACTIONS = [0, 1]  # 0 = no irrigation, 1 = irrigate

# --------------------------------------------------
# HYPERPARAMETERS
# --------------------------------------------------
ALPHA = 0.1
GAMMA = 0.9
EPSILON = 0.1


# --------------------------------------------------
# STATE DISCRETIZATION
# --------------------------------------------------
def discretize_soil_moisture(value):
    if value < 40:
        return "low"
    elif value < 65:
        return "medium"
    else:
        return "high"


def discretize_rainfall(value):
    if value < 30:
        return "low"
    elif value < 80:
        return "medium"
    else:
        return "high"


# --------------------------------------------------
# STATE BUILDER
# --------------------------------------------------
def get_state(data):
    return {
        "soil_moisture_level": discretize_soil_moisture(data["soil_moisture_pct"]),
        "rainfall_level": discretize_rainfall(data["rainfall_mm"]),
        "crop": data["crop"],
        "growth_stage": data["growth_stage"],
        "disease_risk": data["disease_risk"]
    }


# --------------------------------------------------
# FETCH Q-VALUES FROM SUPABASE
# --------------------------------------------------
def fetch_q_values(state):
    response = (
        supabase
        .table(TABLE_NAME)
        .select("action, q_value")
        .eq("soil_moisture_level", state["soil_moisture_level"])
        .eq("rainfall_level", state["rainfall_level"])
        .eq("crop", state["crop"])
        .eq("growth_stage", state["growth_stage"])
        .eq("disease_risk", state["disease_risk"])
        .execute()
    )

    q_values = {0: 0.0, 1: 0.0}

    for row in response.data:
        q_values[row["action"]] = row["q_value"]

    return q_values


# --------------------------------------------------
# ACTION SELECTION (EPSILON-GREEDY)
# --------------------------------------------------
def choose_action(state):
    # Exploration
    if random.random() < EPSILON:
        return random.choice(ACTIONS)

    # Exploitation
    q_values = fetch_q_values(state)
    return max(q_values, key=q_values.get)


# --------------------------------------------------
# Q-LEARNING UPDATE (PERSISTENT)
# --------------------------------------------------
def update_q_table(state, action, reward, next_state=None):
    current_q = fetch_q_values(state)[action]
    
    # If next_state provided, use full Q-learning update
    if next_state:
        next_max_q = max(fetch_q_values(next_state).values())
        new_q = current_q + ALPHA * (reward + GAMMA * next_max_q - current_q)
    else:
        # Simple reward-based update (for feedback without next state)
        new_q = current_q + ALPHA * reward

    # Upsert Q-value
    supabase.table(TABLE_NAME).upsert(
        {
            "soil_moisture_level": state["soil_moisture_level"],
            "rainfall_level": state["rainfall_level"],
            "crop": state["crop"],
            "growth_stage": state["growth_stage"],
            "disease_risk": state["disease_risk"],
            "action": action,
            "q_value": new_q,
            "visit_count": 1
        },
        on_conflict="soil_moisture_level,rainfall_level,crop,growth_stage,disease_risk,action"
    ).execute()


# --------------------------------------------------
# DEBUG / XAI SUPPORT
# --------------------------------------------------
def get_q_values(state):
    return fetch_q_values(state)


def get_q_table():
    """
    Retrieve entire Q-table from Supabase for monitoring.
    Returns limited results to avoid performance issues.
    """
    response = supabase.table(TABLE_NAME).select("*").limit(100).execute()
    return response.data
