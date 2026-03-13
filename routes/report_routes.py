from flask import Blueprint, request, jsonify, make_response, current_app
from services.report_service import get_report_data
import csv
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

report_bp = Blueprint('report', __name__, url_prefix='/api/reports')

@report_bp.route('/preview', methods=['GET'])
def preview():
    """Return JSON data for report preview."""
    try:
        report_type = request.args.get('report_type', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        employee = request.args.get('employee')

        data = get_report_data(report_type, start_date, end_date, department, employee)
        return jsonify(data)
    except Exception as e:
        current_app.logger.error(f"Error in /preview: {e}")
        return jsonify({"error": str(e)}), 500

@report_bp.route('/export/csv', methods=['GET'])
def export_csv():
    """Generate CSV file from filtered data."""
    try:
        report_type = request.args.get('report_type', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        employee = request.args.get('employee')

        data = get_report_data(report_type, start_date, end_date, department, employee)

        # Create CSV in memory
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=['employee','id','department','date','login','logout','status'])
        writer.writeheader()
        writer.writerows(data)

        response = make_response(output.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename=report.csv'
        response.headers['Content-type'] = 'text/csv'
        return response
    except Exception as e:
        current_app.logger.error(f"Error in /export/csv: {e}")
        return jsonify({"error": str(e)}), 500

@report_bp.route('/export/excel', methods=['GET'])
def export_excel():
    """Generate Excel file from filtered data."""
    try:
        report_type = request.args.get('report_type', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        employee = request.args.get('employee')

        data = get_report_data(report_type, start_date, end_date, department, employee)

        # Convert to pandas DataFrame
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Report')
        output.seek(0)

        response = make_response(output.read())
        response.headers['Content-Disposition'] = 'attachment; filename=report.xlsx'
        response.headers['Content-type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        return response
    except Exception as e:
        current_app.logger.error(f"Error in /export/excel: {e}")
        return jsonify({"error": str(e)}), 500

@report_bp.route('/export/pdf', methods=['GET'])
def export_pdf():
    """Generate PDF file from filtered data."""
    try:
        report_type = request.args.get('report_type', 'daily')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        department = request.args.get('department')
        employee = request.args.get('employee')

        data = get_report_data(report_type, start_date, end_date, department, employee)

        # Create PDF with ReportLab
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, f"Attendance Report ({report_type})")
        c.setFont("Helvetica", 10)

        # Table headers
        y = height - 80
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y, "Employee")
        c.drawString(150, y, "ID")
        c.drawString(200, y, "Dept")
        c.drawString(270, y, "Date")
        c.drawString(350, y, "Login")
        c.drawString(410, y, "Logout")
        c.drawString(480, y, "Status")
        y -= 15
        c.setFont("Helvetica", 9)

        for row in data:
            c.drawString(50, y, row['employee'][:15])
            c.drawString(150, y, row['id'])
            c.drawString(200, y, row['department'])
            c.drawString(270, y, row['date'])
            c.drawString(350, y, row['login'] or '')
            c.drawString(410, y, row['logout'] or '')
            c.drawString(480, y, row['status'])
            y -= 15
            if y < 50:  # New page
                c.showPage()
                y = height - 50

        c.save()
        buffer.seek(0)

        response = make_response(buffer.read())
        response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
        response.headers['Content-type'] = 'application/pdf'
        return response
    except Exception as e:
        current_app.logger.error(f"Error in /export/pdf: {e}")
        return jsonify({"error": str(e)}), 500