from flask import Blueprint, jsonify
report_bp = Blueprint('report', __name__)

@report_bp.route('/<type>', methods=['GET'])
def generate_report(type):
    return jsonify({"message": f"Report {type}"}), 200