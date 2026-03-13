from flask import Blueprint, jsonify
analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
def summary():
    # Placeholder – implement as needed
    return jsonify({"message": "Analytics summary"}), 200