# Simple in-memory penalty store
# Key = action, Value = penalty score
POLICY_PENALTIES = {
    1: 0,  # irrigate
    0: 0   # do not irrigate
}

def apply_penalty(action):
    POLICY_PENALTIES[action] += 1

def is_action_allowed(action, threshold=2):
    """
    If penalty crosses threshold, block action
    """
    return POLICY_PENALTIES[action] < threshold

def get_policy_state():
    return POLICY_PENALTIES
