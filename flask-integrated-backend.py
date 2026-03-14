from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import random
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'vibecraft-secret-2024'
CORS(app, resources={r"/*": {"origins": "*"}})

DB_FILE = 'vibecraft.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        phone TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT DEFAULT 'driver',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS otp_verification (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT NOT NULL,
        otp TEXT NOT NULL,
        purpose TEXT,
        expires_at TIMESTAMP,
        verified INTEGER DEFAULT 0
    )''')
    
    # Demo users
    demo_users = [
('driver', 'driver@vibecraft.com', '+919876543210', hashlib.sha256('Driver@123'.encode()).hexdigest(), 'driver', datetime.now()),
('admin', 'admin@vibecraft.com', '+919876543211', hashlib.sha256('Admin@123'.encode()).hexdigest(), 'admin', datetime.now())
    ]
    
    for user in demo_users:
        c.execute('INSERT OR IGNORE INTO users (username, email, phone, password_hash, role, created_at) VALUES (?, ?, ?, ?, ?, ?)', (user[0], user[1], user[2], user[3], user[4], user[5]))
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health():
    return jsonify({'success': True, 'message': 'Backend ready', 'data': {'status': 'active'}}), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').lower().strip()
        password = data.get('password', '')
        role = data.get('role', 'driver')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, role)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        if hashlib.sha256(password.encode()).hexdigest() != user['password_hash']:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        session_token = hashlib.sha256(f"{username}{datetime.now().timestamp()}".encode()).hexdigest()[:32]
        session['user_id'] = user['id']
        session['username'] = username
        session['role'] = role
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'username': username,
                'role': role,
                'phone': user['phone'],
                'session_token': session_token
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        username = data.get('username', '').lower().strip()
        email = data.get('email', '').strip()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        role = data.get('role', 'driver')
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password too short'}), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)',
                        (username, email, phone, password_hash, role))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Registration successful'}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Username or phone already exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/auth/send-sms-otp', methods=['POST'])
def send_sms_otp():
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        purpose = data.get('purpose', 'reset')
        
        otp = str(random.randint(100000, 999999))
        expires_at = datetime.now() + timedelta(minutes=5)
        
        conn = get_db_connection()
        conn.execute('INSERT INTO otp_verification (phone, otp, purpose, expires_at) VALUES (?, ?, ?, ?)',
                    (phone, otp, purpose, expires_at))
        conn.commit()
        conn.close()
        
        print(f"📱 Simulated SMS to {phone}: OTP = {otp}")
        
        return jsonify({
            'success': True,
            'message': 'OTP sent to phone (check terminal)',
            'data': {'debug_otp': otp}  # Frontend can show this for demo
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/auth/verify-sms-otp', methods=['POST'])
def verify_sms_otp():
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '')
        purpose = data.get('purpose', 'reset')
        
        conn = get_db_connection()
        record = conn.execute('''
            SELECT * FROM otp_verification 
            WHERE phone = ? AND otp = ? AND purpose = ? AND verified = 0
            ORDER BY id DESC LIMIT 1
        ''', (phone, otp, purpose)).fetchone()
        
        if record:
            conn.execute('UPDATE otp_verification SET verified = 1 WHERE id = ?', (record['id'],))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'OTP verified successfully'}), 200
        
        conn.close()
        return jsonify({'success': False, 'message': 'Invalid or expired OTP'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/auth/reset-password-phone', methods=['POST'])
def reset_password_phone():
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        password = data.get('password', '')
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        conn.execute('UPDATE users SET password_hash = ? WHERE phone = ?', (password_hash, phone))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Password reset successful'}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/ambulance/live-location', methods=['POST'])
def ambulance_location():
    try:
        data = request.get_json()
        lat = data.get('lat')
        lng = data.get('lng')
        speed = data.get('speed', 0)
        
        # Simulate traffic signal logic
        signals = [
            {'id': 'S1', 'lat': 17.3845, 'lng': 78.4867, 'distance': abs(lat - 17.3845)*111000, 'state': 'GREEN' if abs(lat - 17.3845) < 0.0003 else 'RED'},
            {'id': 'S2', 'lat': 17.3855, 'lng': 78.4867, 'distance': abs(lat - 17.3855)*111000, 'state': 'GREEN' if abs(lat - 17.3855) < 0.0003 else 'RED'},
            {'id': 'S3', 'lat': 17.3865, 'lng': 78.4867, 'distance': abs(lat - 17.3865)*111000, 'state': 'GREEN' if abs(lat - 17.3865) < 0.0003 else 'RED'}
        ]
        
        nearest = min(signals, key=lambda s: s['distance'])
        
        return jsonify({
            'success': True,
            'message': 'Location updated',
            'data': {
                'lat': lat,
                'lng': lng,
                'speed': speed,
                'nearest_signal': nearest,
                'all_signals': signals
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    try:
        # Check session
        if 'user_id' not in session or session.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Admin access required'}), 403
        
        conn = get_db_connection()
        users = conn.execute('SELECT username, role, phone FROM users').fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'users': [dict(u) for u in users],
                'active_ambulances': 3,
                'signals_active': 7,
                'priority_success': '92%'
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/ambulance/active', methods=['GET'])
def active_ambulances():
    try:
        return jsonify({
            'success': True,
            'data': {
                'ambulances': [
                    {'id': 'AMB001', 'lat': 17.3852, 'lng': 78.4867, 'status': 'active', 'eta': '4m 23s'},
                    {'id': 'AMB002', 'lat': 17.3848, 'lng': 78.4867, 'status': 'active', 'eta': '6m 12s'}
                ]
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

if __name__ == '__main__':
    init_db()
    print('🚑 VibeCraft Backend LIVE on http://127.0.0.1:5000')
    print('Demo login: driver / Driver@123')
    app.run(host='127.0.0.1', port=5000, debug=True)

