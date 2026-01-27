import random


# Action space
# 0 = Do not irrigate
# 1 = Irrigate
ACTIONS = [0, 1]


def get_state(data):
    """
    Convert farm data into an RL-friendly state tuple.

    data: dict with farm_data.csv fields
    """

    return (
        data["soil_moisture_pct"],
        data["rainfall_mm"],
        data["temperature_c"],
        data["humidity_pct"],
        data["crop"],
        data["growth_stage"],
        data["disease_risk"],
        data["pest_risk"]
    )


def choose_action(state, epsilon=0.1):
    """
    Epsilon-greedy policy.

    state: output of get_state()
    epsilon: exploration rate
    """

    # Exploration
    if random.random() < epsilon:
        return random.choice(ACTIONS)

    # Exploitation (simple heuristic-based policy for now)
    soil_moisture = state[0]
    rainfall = state[1]
    disease_risk = state[6]

    # Heuristic rules
    if rainfall >= 80:
        return 0

    if soil_moisture < 45 and disease_risk != "high":
        return 1

    return 0


def update_policy(state, action, regret):
    """
    Placeholder for future learning logic.

    state: RL state
    action: action taken
    regret: regret score from regret_engine
    """

    # Future scope:
    # - Q-learning
    # - Policy gradient
    # - Regret minimization

    pass
