from flask import Blueprint, jsonify, request
settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/', methods=['GET'])
def get_settings():
    return jsonify({"office_start": "09:00", "late_threshold": "09:15"}), 200

@settings_bp.route('/', methods=['POST'])
def update_settings():
    return jsonify({"message": "Settings updated"}), 200