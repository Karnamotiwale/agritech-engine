# Q-table: State → Action → Value
Q_TABLE = {
    "dry_hot": {0: 0, 1: 0},
    "wet_rain": {0: 0, 1: 0},
    "normal": {0: 0, 1: 0}
}

LEARNING_RATE = 0.3


def get_state(data):
    if data["soil_moisture"] < 30 and data["temperature"] > 32:
        return "dry_hot"
    if data["rain_forecast"] == 1:
        return "wet_rain"
    return "normal"


def choose_action(state):
    """
    Choose action with highest Q-value
    """
    actions = Q_TABLE[state]
    return max(actions, key=actions.get)


def update_q_table(state, action, reward):
    """
    Q-learning update (simplified)
    """
    old_value = Q_TABLE[state][action]
    Q_TABLE[state][action] = old_value + LEARNING_RATE * (reward - old_value)


def get_q_table():
    return Q_TABLE
