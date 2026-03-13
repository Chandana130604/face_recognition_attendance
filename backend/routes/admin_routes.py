from flask import Blueprint, jsonify

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/stats', methods=['GET'])
def stats():
    # Placeholder – implement later
    return jsonify({"message": "Admin stats (placeholder)"}), 200