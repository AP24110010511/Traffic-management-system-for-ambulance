from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import random
import math
import secrets

app = Flask(__name__)
CORS(app, resources={"*": {"origins": "*"}})

DB_PATH = 'traffic_system.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        role TEXT,
        session_token TEXT,
        last_login TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS otps (
        phone TEXT PRIMARY KEY,
        otp TEXT,
        expires TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS ambulance (
        id TEXT PRIMARY KEY,
        lat REAL,
        lon REAL,
        speed REAL,
        hospital TEXT,
        eta REAL,
        status TEXT,
        updated TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY,
        name TEXT,
        lat REAL,
        lon REAL,
        state TEXT DEFAULT 'RED',
        controlled_by TEXT
    )''')
    # Demo signals data
    signals_data = [
        (1, 'Main Road Signal', 17.3850, 78.4860, 'RED', None),
        (2, 'Hospital Approach', 17.3840, 78.4870, 'RED', None),
        (3, 'City Center', 17.3860, 78.4850, 'RED', None)
    ]
    c.executemany('INSERT OR IGNORE INTO signals VALUES (?,?,?,?,?,?)', signals_data)
    conn.commit()
    conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def generate_otp():
    return str(random.randint(1000, 9999))

@app.route('/health')
def health():
    return jsonify({
        "success": True,
        "message": "Smart Traffic System is running",
        "data": {}
    })

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data or 'phone' not in data or 'role' not in data:
            return jsonify({"success": False, "message": "Missing phone or role", "data": {}}), 400
        
        phone = data['phone'].strip()
        role = data['role']
        if len(phone) == 10:
            phone = '+91' + phone.lstrip('0')
        
        otp = generate_otp()
        expires = (datetime.now() + timedelta(minutes=5)).isoformat()
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO otps (phone, otp, expires) VALUES (?, ?, ?)', (phone, otp, expires))
        c.execute('INSERT OR IGNORE INTO users (phone, role) VALUES (?, ?)', (phone, role))
        conn.commit()
        conn.close()
        
        print(f"📱 OTP {otp} sent to {phone} ({role})")  # Mock SMS
        
        return jsonify({
            "success": True,
            "message": "OTP sent successfully",
            "data": {"phone": phone, "role": role}
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Login error: {str(e)}", "data": {}}), 500

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        if not data or 'phone' not in data or 'otp' not in data:
            return jsonify({"success": False, "message": "Missing phone or OTP", "data": {}}), 400
        
        phone = data['phone']
        otp = data['otp']
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT otp, expires FROM otps WHERE phone = ?', (phone,))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({"success": False, "message": "No OTP found", "data": {}}), 400
        
        stored_otp, expires_str = row
        expires = datetime.fromisoformat(expires_str)
        
        if datetime.now() > expires:
            return jsonify({"success": False, "message": "OTP expired", "data": {}}), 400
        if stored_otp != otp:
            return jsonify({"success": False, "message": "Invalid OTP", "data": {}}), 400
        
        # Generate session token
        token = secrets.token_hex(16)
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('UPDATE users SET session_token = ?, last_login = ? WHERE phone = ?', 
                  (token, datetime.now().isoformat(), phone))
        c.execute('DELETE FROM otps WHERE phone = ?', (phone,))
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Login successful",
            "data": {"session_token": token, "phone": phone}
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Verification error: {str(e)}", "data": {}}), 500

@app.route('/api/update-location', methods=['POST'])
def update_location():
    try:
        data = request.get_json()
        if not all(k in data for k in ['lat', 'lon', 'id', 'hospital']):
            return jsonify({"success": False, "message": "Missing lat, lon, id, or hospital", "data": {}}), 400
        
        lat = float(data['lat'])
        lon = float(data['lon'])
        ambulance_id = data['id']
        hospital = data['hospital']
        speed = data.get('speed', 40.0)
        
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        # Check nearby signals and turn GREEN
        c.execute('SELECT id, name, lat, lon FROM signals')
        signals = c.fetchall()
        green_signals = []
        min_dist = float('inf')
        nearest_signal = None
        
        for sig_id, sig_name, sig_lat, sig_lon in signals:
            dist = haversine(lat, lon, sig_lat, sig_lon)
            if dist < 300:  # Within 300m
                c.execute('UPDATE signals SET state = "GREEN", controlled_by = ? WHERE id = ?', 
                         (ambulance_id, sig_id))
                green_signals.append(sig_name)
            if dist < min_dist:
                min_dist = dist
                nearest_signal = sig_name
        
        # Calculate ETA to nearest signal
        eta = (min_dist / speed) * 60  # minutes
        
        # Update ambulance status
        c.execute('''INSERT OR REPLACE INTO ambulance 
                     (id, lat, lon, speed, hospital, eta, status, updated) 
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
                 (ambulance_id, lat, lon, speed, hospital, eta, 'active', datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Location updated, signals prioritized",
            "data": {
                "eta": round(eta, 1),
                "green_signals": green_signals,
                "nearest_signal": nearest_signal
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Update failed: {str(e)}", "data": {}}), 500

@app.route('/api/ambulance-status', methods=['GET'])
def ambulance_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT id, lat, lon, speed, hospital, eta, status FROM ambulance ORDER BY updated DESC')
        rows = c.fetchall()
        columns = [description[0] for description in c.description]
        data = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return jsonify({
            "success": True,
            "message": "Ambulance status fetched",
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Status error: {str(e)}", "data": {}}), 500

@app.route('/api/signal-status', methods=['GET'])
def signal_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT * FROM signals')
        rows = c.fetchall()
        columns = [description[0] for description in c.description]
        data = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return jsonify({
            "success": True,
            "message": "Signal status fetched",
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Signal error: {str(e)}", "data": {}}), 500

@app.route('/api/eta', methods=['GET'])
def eta():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('SELECT hospital, eta FROM ambulance ORDER BY updated DESC LIMIT 1')
        row = c.fetchone()
        conn.close()
        if row:
            return jsonify({
                "success": True,
                "message": "ETA fetched",
                "data": {"hospital": row[0], "eta_minutes": round(row[1], 1)}
            })
        return jsonify({
            "success": True,
            "message": "No active ambulance",
            "data": {"eta_minutes": 0}
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"ETA error: {str(e)}", "data": {}}), 500

@app.route('/api/hospital-alert', methods=['POST'])
def hospital_alert():
    try:
        data = request.get_json()
        ambulance_id = data['ambulance_id']
        hospital = data['hospital']
        eta = data.get('eta', 0)
        
        print(f"🚨 HOSPITAL ALERT: Ambulance {ambulance_id} ETA {eta}min to {hospital}")
        print("📲 Notification sent to hospital staff!")
        
        return jsonify({
            "success": True,
            "message": "Hospital notified successfully",
            "data": {"ambulance_id": ambulance_id, "hospital": hospital, "eta": eta}
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Alert failed: {str(e)}", "data": {}}), 500

if __name__ == '__main__':
    init_db()
    print("🚑 Smart Traffic Backend running on http://127.0.0.1:5000")
    print("Test: curl http://127.0.0.1:5000/health")
    app.run(host='127.0.0.1', port=5000, debug=True)
