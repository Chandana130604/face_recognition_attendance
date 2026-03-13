from flask import Blueprint, jsonify

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/summary', methods=['GET'])
def summary():
    return jsonify({"message": "Analytics summary (placeholder)"}), 200