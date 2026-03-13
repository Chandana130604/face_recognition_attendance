from flask import Flask, render_template, session, redirect, url_for
from backend.auth import auth_bp
from backend.employee_manager import EmployeeManager
from backend.attendance_manager import AttendanceManager
from datetime import datetime
from config import Config

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object(Config)
app.secret_key = Config.SECRET_KEY
app.permanent_session_lifetime = Config.SESSION_TIMEOUT

# Register blueprints
app.register_blueprint(auth_bp)

emp_mgr = EmployeeManager()
att_mgr = AttendanceManager()

# Session timeout middleware (simple check)
@app.before_request
def check_session_timeout():
    # This can be implemented via Flask's session.permanent and permanent_session_lifetime
    pass

@app.route('/admin-dashboard')
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('auth.login'))
    employees = emp_mgr.get_all_employees()
    today = datetime.now().strftime('%Y-%m-%d')
    attendance = att_mgr.get_daily_attendance(today)
    present = len([a for a in attendance if a.get('status') == 'Present'])
    stats = {
        'total_employees': len(employees),
        'present_today': present,
        'absent_today': len(employees) - present
    }
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/employee-dashboard')
def employee_dashboard():
    if 'user_id' not in session or session.get('role') != 'employee':
        return redirect(url_for('auth.login'))
    emp_id = session.get('employee_id')
    employee = emp_mgr.get_employee_by_emp_id(emp_id) if emp_id else None
    return render_template('employee_dashboard.html', employee=employee)

if __name__ == '__main__':
    app.run(debug=True)