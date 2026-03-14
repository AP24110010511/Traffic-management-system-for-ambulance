from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import hashlib
import random
import os
from datetime import datetime, timedelta
import sys

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DB_FILE = 'users.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT DEFAULT 'driver',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_verification (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            otp TEXT NOT NULL,
            purpose TEXT,
            expires_at TIMESTAMP,
            verified INTEGER DEFAULT 0
        )
    ''')
    
    # Demo users
    demo_data = [
        ('driver', 'driver@test.com', '+919999999998', hashlib.sha256('Driver@123'.encode()).hexdigest(), 'driver'),
        ('admin', 'admin@test.com', '+919999999999', hashlib.sha256('Admin@123'.encode()).hexdigest(), 'admin')
    ]
    
    for user in demo_data:
        cursor.execute('INSERT OR IGNORE INTO users (username, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)', user)
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/health')
def health():
    return jsonify({'success': True, 'status': 'Backend ready', 'port': 5000})

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').lower().strip()
        password = data.get('password', '')
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        
        if not user:
            return jsonify({'success': False, 'message': 'User not found'}), 401
        
        if hashlib.sha256(password.encode()).hexdigest() != user['password_hash']:
            return jsonify({'success': False, 'message': 'Incorrect password'}), 401
        
        token = hashlib.sha256(f"{username}{datetime.now()}".encode()).hexdigest()[:32]
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'data': {
                'username': user['username'],
                'role': user['role'],
                'phone': user['phone'],
                'session_token': token
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
        
        if len(password) < 8:
            return jsonify({'success': False, 'message': 'Password too short'}), 400
        
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, phone, password_hash, role) VALUES (?, ?, ?, ?, ?)', 
                        (username, email, phone, password_hash, data.get('role', 'driver')))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Registered successfully'}), 201
        except sqlite3.IntegrityError:
            conn.close()
            return jsonify({'success': False, 'message': 'Username or phone exists'}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/auth/send-sms-otp', methods=['POST'])
def send_sms_otp():
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        otp = str(random.randint(100000, 999999))
        
        conn = get_db_connection()
        conn.execute('INSERT INTO otp_verification (phone, otp, purpose, expires_at) VALUES (?, ?, ?, ?)',
                    (phone, otp, 'reset', datetime.now() + timedelta(minutes=5)))
        conn.commit()
        conn.close()
        
        # Simulate SMS
        print(f"📱 SMS OTP {otp} to {phone}")
        
        return jsonify({
            'success': True,
            'message': 'OTP sent (check console)',
            'debug_otp': otp
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/auth/verify-sms-otp', methods=['POST'])
def verify_sms_otp():
    try:
        data = request.get_json()
        phone = data.get('phone', '').strip()
        otp = data.get('otp', '')
        
        conn = get_db_connection()
        record = conn.execute('SELECT * FROM otp_verification WHERE phone = ? AND otp = ? AND verified = 0 ORDER BY id DESC LIMIT 1', 
                            (phone, otp)).fetchone()
        conn.close()
        
        if record:
            return jsonify({'success': True, 'message': 'OTP verified'}), 200
        
        return jsonify({'success': False, 'message': 'Invalid OTP'}), 400
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

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        conn = get_db_connection()
        users = conn.execute('SELECT username, role, phone FROM users').fetchall()
        conn.close()
        return jsonify({'success': True, 'users': [dict(u) for u in users]}), 200
    except Exception as e:
        return jsonify({'success': False, 'message': 'Server error'}), 500

if __name__ == '__main__':
    init_db()
    print('🚑 Backend ready on http://localhost:5000')
    print('Demo: driver / Driver@123')
    app.run(host='0.0.0.0', port=5000, debug=True)

