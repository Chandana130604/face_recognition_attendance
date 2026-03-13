from flask import Blueprint, jsonify

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/stats', methods=['GET'])
def stats():
    return jsonify({"message": "Admin stats (placeholder)"}), 200