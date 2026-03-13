from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file, flash
from database.mongodb_connection import Database
from backend.face_utils import FaceUtils
from backend.attendance_manager import AttendanceManager
from backend.employee_manager import EmployeeManager
from backend.user_manager import UserManager
from backend.auth import auth_bp
from datetime import datetime, timedelta
import os
import base64
import logging
import traceback
import numpy as np
import json
import cv2
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change in production

# Increase max request size to 100 MB (for 20‑frame registration)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Custom error handler for request entity too large (413)
@app.errorhandler(413)
def request_entity_too_large(error):
    app.logger.error(f"413 Request Entity Too Large: Content-Length = {request.headers.get('Content-Length', 'unknown')}")
    return jsonify({'error': 'Uploaded images are too large. Please reduce image quality or number of frames.'}), 413

# Setup logging
logging.basicConfig(level=logging.DEBUG)

# Initialize managers
emp_mgr = EmployeeManager()
att_mgr = AttendanceManager()
face_utils = FaceUtils()
user_mgr = UserManager()

# Register authentication blueprint
app.register_blueprint(auth_bp)

# ------------------ Cache for known encodings ------------------
known_encodings = []
known_employee_ids = []
known_names = []

def refresh_known_faces():
    """Load all employee face encodings from MongoDB into memory."""
    global known_encodings, known_employee_ids, known_names
    known_encodings = []
    known_employee_ids = []
    known_names = []
    employees = emp_mgr.get_all_employees()
    for emp in employees:
        for enc in emp.face_encodings:
            known_encodings.append(enc)
            known_employee_ids.append(emp.emp_id)
            known_names.append(emp.name)
    app.logger.debug(f"Loaded {len(known_encodings)} face encodings.")

# Load on startup
refresh_known_faces()
# ----------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin-register', methods=['GET', 'POST'])
def admin_register():
    """Register a new admin user."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            return render_template('admin_register.html', error='Passwords do not match')
        try:
            user_mgr.register_admin(username, password)
            return redirect(url_for('admin_login'))
        except ValueError as e:
            return render_template('admin_register.html', error=str(e))
    return render_template('admin_register.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if user_mgr.authenticate(username, password):
            session['admin'] = True
            session['username'] = username
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid credentials')
    return render_template('admin_login.html')

@app.route('/admin-dashboard')
def admin_dashboard():
    """Admin dashboard with stats, recent activity, and attendance chart."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    employees = emp_mgr.get_all_employees()
    today = datetime.now().strftime('%Y-%m-%d')
    attendance = att_mgr.get_daily_attendance(today)
    present = len([a for a in attendance if a.get('status') == 'Present'])
    total = len(employees)
    absent = total - present
    attendance_percent = (present / total * 100) if total > 0 else 0

    stats = {
        'total_employees': total,
        'present_today': present,
        'absent_today': absent
    }
    
    current_time = datetime.now().strftime('%H:%M')
    today_date = datetime.now().strftime('%B %d, %Y')
    
    # Recent attendance (last 5 records from last 7 days)
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
    all_recent = att_mgr.get_attendance_range(seven_days_ago, today)
    recent_attendance = all_recent[-5:] if all_recent else []
    
    # Chart data for last 7 days
    chart_labels = []
    chart_data = []
    for i in range(6, -1, -1):
        day = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
        chart_labels.append(day)
        day_att = att_mgr.get_daily_attendance(day)
        chart_data.append(len([a for a in day_att if a.get('status') == 'Present']))
    
    return render_template('admin_dashboard.html',
                           stats=stats,
                           current_time=current_time,
                           recent_attendance=recent_attendance,
                           chart_labels=chart_labels,
                           chart_data=chart_data,
                           attendance_percent=attendance_percent,
                           today_date=today_date)

@app.route('/profile', methods=['GET'])
def profile():
    """Admin profile page."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('profile.html')

@app.route('/update-profile', methods=['POST'])
def update_profile():
    """Handle profile update form."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    # Placeholder – you can implement actual update logic here
    flash('Profile updated successfully (demo).', 'success')
    return redirect(url_for('profile'))

@app.route('/settings', methods=['GET'])
def settings():
    """Admin settings page."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    return render_template('settings.html')

@app.route('/change-password', methods=['POST'])
def change_password():
    """Handle password change."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    current = request.form['current_password']
    new = request.form['new_password']
    confirm = request.form['confirm_password']
    if new != confirm:
        flash('New passwords do not match.', 'danger')
        return redirect(url_for('settings'))
    # Here you would verify current password and update
    flash('Password changed successfully (demo).', 'success')
    return redirect(url_for('settings'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Employee registration with multiple face captures."""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        name = request.form['name']
        dept = request.form['department']
        email = request.form.get('email', '')
        role = request.form['role']
        images_json = request.form['images']
        image_urls = json.loads(images_json)

        encodings = []
        for img_url in image_urls:
            image_data = img_url.split(',')[1]
            image_bytes = base64.b64decode(image_data)
            encoding = face_utils.get_face_encoding(image_bytes)
            if encoding is not None:
                encodings.append(encoding)
        if len(encodings) == 0:
            return render_template('register_employee.html', error='No valid face detected in any image.')
        try:
            emp_mgr.add_employee(emp_id, name, dept, email, role, encodings)
            refresh_known_faces()
            return redirect(url_for('admin_dashboard'))
        except Exception as e:
            app.logger.error(f"Error registering employee: {e}")
            return render_template('register_employee.html', error=str(e))
    
    return render_template('register_employee.html')

@app.route('/face-login')
def face_login_page():
    return render_template('face_login.html')

@app.route('/api/recognize', methods=['POST'])
def recognize():
    """
    Enhanced face recognition endpoint using MTCNN + face_recognition.
    Returns check-in/check-out status and sets employee session.
    """
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image data'}), 400

        img_data = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        img_bytes = base64.b64decode(img_data)

        # Get face encoding using enhanced method
        face_encoding = face_utils.get_face_encoding(img_bytes)
        if face_encoding is None:
            return jsonify({'status': 'no_face'})

        # Compare with known encodings
        idx, distance = face_utils.compare_faces(known_encodings, face_encoding)
        if idx is None:
            return jsonify({'status': 'unknown'})

        employee_id = known_employee_ids[idx]
        name = known_names[idx]

        # Determine check-in or check-out
        today_att = att_mgr.get_today_attendance(employee_id)
        action = None
        if today_att:
            if today_att.get('check_out_time') is None:
                # Already checked in, so this is check-out
                att_mgr.check_out(employee_id)
                action = 'checkout'
            else:
                # Already checked out – ignore (no change)
                action = 'already_logged_out'
        else:
            # No attendance today → check-in
            att_mgr.check_in(employee_id)
            action = 'checkin'

        # Set employee session (allow dashboard access regardless)
        session['employee_id'] = employee_id
        session['employee_name'] = name
        session['employee_logged_in'] = True

        return jsonify({
            'status': 'success',
            'employee_id': employee_id,
            'name': name,
            'action': action,
            'distance': float(distance)
        })

    except Exception as e:
        err = traceback.format_exc()
        print("RECOGNIZE ERROR:", err)
        app.logger.error(f"Error in /api/recognize: {err}")
        return jsonify({'error': str(e), 'trace': err}), 500

@app.route('/employee-dashboard')
def employee_dashboard():
    """Employee dashboard showing personal attendance records."""
    if not session.get('employee_logged_in'):
        return redirect(url_for('face_login_page'))
    
    employee_id = session.get('employee_id')
    name = session.get('employee_name')
    
    # Get last 30 days attendance
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    attendance = att_mgr.get_employee_attendance(employee_id, start_date, end_date)
    
    return render_template('employee_dashboard.html',
                           name=name,
                           emp_id=employee_id,
                           attendance=attendance)

@app.route('/employee-logout')
def employee_logout():
    """Logout employee and redirect to face login page."""
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    session.pop('employee_logged_in', None)
    return redirect(url_for('face_login_page'))

@app.route('/api/attendance/today-pie')
def today_attendance_pie():
    """Return JSON with present and absent counts for today."""
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    today = datetime.now().strftime('%Y-%m-%d')
    attendance = att_mgr.get_daily_attendance(today)
    present = len([a for a in attendance if a.get('status') == 'Present'])
    total_employees = len(emp_mgr.get_all_employees())
    absent = total_employees - present
    return jsonify({'present': present, 'absent': absent})

@app.route('/attendance')
def attendance_logs():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    records = att_mgr.get_daily_attendance(date_str)
    return render_template('attendance_logs.html', records=records, selected_date=date_str)

@app.route('/export-csv')
def export_csv():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    filepath = f'reports/attendance_{date_str}.csv'
    try:
        att_mgr.export_to_csv(date_str, filepath)
        return send_file(filepath, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Error exporting CSV: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    """Admin logout."""
    session.pop('admin', None)
    session.pop('username', None)
    return redirect(url_for('admin_login'))

@app.route('/employees')
def employee_list():
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    employees = emp_mgr.get_all_employees()
    return render_template('employees.html', employees=employees)

@app.route('/employee/<emp_id>')
def employee_detail(emp_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    employee = emp_mgr.get_employee_by_emp_id(emp_id)
    if not employee:
        return "Employee not found", 404
    return render_template('employee_detail.html', emp=employee)

@app.route('/employee/<emp_id>/edit', methods=['GET', 'POST'])
def edit_employee(emp_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    employee = emp_mgr.get_employee_by_emp_id(emp_id)
    if not employee:
        return "Employee not found", 404
    if request.method == 'POST':
        # update logic – you can implement update_employee in manager
        return redirect(url_for('employee_list'))
    return render_template('edit_employee.html', emp=employee)

@app.route('/employee/<emp_id>/delete', methods=['POST'])
def delete_employee(emp_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    emp_mgr.delete_employee(emp_id)
    refresh_known_faces()
    return redirect(url_for('employee_list'))

@app.route('/recapture/<emp_id>', methods=['GET', 'POST'])
def recapture_face(emp_id):
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    employee = emp_mgr.get_employee_by_emp_id(emp_id)
    if not employee:
        return "Employee not found", 404
    if request.method == 'POST':
        image_data = request.form['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)
        encoding = face_utils.get_face_encoding(image_bytes)
        if encoding is None:
            return render_template('recapture.html', employee=employee, error='No face detected')
        emp_mgr.update_encoding(emp_id, [encoding])
        refresh_known_faces()
        return redirect(url_for('employee_list'))
    return render_template('recapture.html', employee=employee)

@app.route('/test-upload', methods=['GET', 'POST'])
def test_upload():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            image_bytes = file.read()
            encoding = face_utils.get_face_encoding(image_bytes)
            if encoding:
                return "✅ Face detected! Encoding length: " + str(len(encoding))
            else:
                return "❌ No face detected in uploaded image."
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Test Face Upload</title></head>
    <body>
        <h2>Upload a clear face photo</h2>
        <form method="post" enctype="multipart/form-data">
            <input type="file" name="image" accept="image/*">
            <input type="submit">
        </form>
    </body>
    </html>
    '''

@app.route('/ping')
def ping():
    return "pong"

# Optional: Debug route to check cache size
@app.route('/debug/cache')
def debug_cache():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({
        'count': len(known_encodings),
        'employee_ids': known_employee_ids,
        'names': known_names
    })

if __name__ == '__main__':
    app.run(debug=True)