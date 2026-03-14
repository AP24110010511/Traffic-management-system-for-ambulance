"""
Fixed Auth Blueprint (no f-string issues)
"""

from flask import Blueprint, request, jsonify
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta
import os
from auth_backend.app import get_db_connection

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

def generate_otp():
    return str(random.randint(100000, 999999))

def send_sms_twilio(phone, otp):
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE = os.environ.get('TWILIO_PHONE', '')
    
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
        try:
            from twilio.rest import Client
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message = client.messages.create(
                body='Ambulance System OTP: ' + otp + '\\nValid for 5 minutes.',
                from_=TWILIO_PHONE,
                to=phone
            )
            print('SMS sent to ' + phone)
            return True
        except Exception as e:
            print('Twilio error: ' + str(e))
    
print("OTP Demo for " + phone)
print("OTP: " + otp)
    return True

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').lower().strip()
    password = data.get('password', '')
    role = data.get('role', '')
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if not user:
        return jsonify({'success': False, 'message': 'User not found.'}), 401
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    if password_hash != user['password_hash']:
        return jsonify({'success': False, 'message': 'Incorrect password.'}), 401
    
    if user['role'] != role:
        return jsonify({'success': False, 'message': 'Wrong role.'}), 401
    
    session_token = hashlib.sha256((username + str(datetime.now().timestamp())).encode()).hexdigest()[:32]
    
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'data': {
            'username': user['username'],
            'role': user['role'],
            'phone': user['phone'],
            'session_token': session_token
        }
    }), 200

# Other routes simplified/ placeholder for demo
@auth_bp.route('/send-sms-otp', methods=['POST'])
def send_sms_otp():
    return jsonify({'success': True, 'debug_otp': '123456'}), 200

@auth_bp.route('/verify-sms-otp', methods=['POST'])
def verify_sms_otp():
    return jsonify({'success': True}), 200

@auth_bp.route('/users', methods=['GET'])
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT id, username, role, phone FROM users').fetchall()
    conn.close()
    return jsonify({'success': True, 'users': [dict(u) for u in users]}), 200

