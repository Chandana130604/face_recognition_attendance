from flask import Blueprint, request, jsonify, current_app
from services.settings_service import SettingsService

settings_bp = Blueprint('settings', __name__, url_prefix='/api/settings')

@settings_bp.route('', methods=['GET'])
def get_settings():
    """Return current system settings."""
    try:
        settings = SettingsService.get_current()
        return jsonify(settings)
    except Exception as e:
        current_app.logger.error(f"Error in GET /api/settings: {e}")
        return jsonify({"error": "Internal server error"}), 500

@settings_bp.route('', methods=['POST'])
def save_settings():
    """Save system settings."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    try:
        result = SettingsService.save(data)
        if result["success"]:
            return jsonify({"message": result["message"]}), 200
        else:
            return jsonify({"error": result["error"]}), 400
    except Exception as e:
        current_app.logger.error(f"Error in POST /api/settings: {e}")
        return jsonify({"error": "Internal server error"}), 500