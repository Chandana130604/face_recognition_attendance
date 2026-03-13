from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database.user_repository import UserRepository
from backend.employee_manager import EmployeeManager
from backend.face_engine import FaceEngine
from models.user import User
from datetime import datetime, timedelta
from config import Config
import base64

auth_bp = Blueprint('auth', __name__)

user_repo = UserRepository()
emp_mgr = EmployeeManager()
face_engine = FaceEngine()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'

        # Input validation
        if not username or not password:
            return render_template('login.html', error='Username and password required')

        user = user_repo.find_by_username(username)
        if not user:
            return render_template('login.html', error='Invalid username or password')

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now():
            return render_template('login.html', error=f'Account locked until {user.locked_until.strftime("%H:%M")}')

        # Verify password
        if not check_password_hash(user.password_hash, password):
            # Increment failed attempts
            attempts = user.failed_attempts + 1
            locked_until = None
            if attempts >= Config.MAX_LOGIN_ATTEMPTS:
                locked_until = datetime.now() + timedelta(minutes=15)  # lock for 15 minutes
            user_repo.update_failed_attempts(username, attempts, locked_until)
            return render_template('login.html', error='Invalid username or password')

        # Success – reset failed attempts and set session
        user_repo.reset_failed_attempts(username)
        user_repo.update_last_login(username)

        session.permanent = True if remember else False
        session['user_id'] = user._id
        session['username'] = user.username
        session['role'] = user.role
        session['employee_id'] = user.employee_id

        # Redirect based on role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('employee_dashboard'))

    return render_template('login.html')

@auth_bp.route('/face-login', methods=['POST'])
def face_login():
    """API endpoint for face recognition login"""
    try:
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'success': False, 'message': 'No image data'}), 400

        # Decode image
        image_data = data['image'].split(',')[1]
        image_bytes = base64.b64decode(image_data)

        # Recognize face using face_engine (needs access to employee encodings)
        emp_id, name = face_engine.recognize_face(image_bytes, emp_mgr)

        if emp_id is None:
            return jsonify({'success': False, 'message': 'Face not recognized'})

        # Find associated user account for this employee
        user = user_repo.find_by_username(emp_id)  # assuming emp_id is used as username
        if not user:
            return jsonify({'success': False, 'message': 'No user account linked to this face'})

        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now():
            return jsonify({'success': False, 'message': 'Account is locked'})

        # Success – set session
        session['user_id'] = user._id
        session['username'] = user.username
        session['role'] = user.role
        session['employee_id'] = user.employee_id
        user_repo.update_last_login(user.username)

        return jsonify({
            'success': True,
            'role': user.role,
            'redirect': '/admin-dashboard' if user.role == 'admin' else '/employee-dashboard'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))