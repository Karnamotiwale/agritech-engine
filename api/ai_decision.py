from flask import Blueprint, request, jsonify
from core.decision_engine import decide_action

ai_decision_bp = Blueprint('ai_decision', __name__)

@ai_decision_bp.route('/irrigationDecision', methods=['POST'])
def irrigation_decision():
    data = request.json or {}
    try:
        # Reusing the upgraded decide_action which now utilizes ask_ai
        decision = decide_action(0, data)
        return jsonify(decision), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
