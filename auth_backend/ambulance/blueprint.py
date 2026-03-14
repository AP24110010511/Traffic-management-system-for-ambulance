"""
Ambulance Blueprint
1. POST /api/ambulance/start {session_token, ambulance_id} → active status
2. POST /api/ambulance/location {session_token, lat, lon, speed} → update, trigger geofence
3. GET /api/ambulance/active → list live ambulances
"""

from flask import Blueprint, request, jsonify
import sys
sys.path.append('.')
from utils.db import get_db_connection
from utils.distance import haversine_distance, calculate_eta
from utils.notifications import hospital_notification, signal_alert, store_alert
import sqlite3
from datetime import datetime

ambulance_bp = Blueprint('ambulance', __name__, url_prefix='/api/ambulance')

@ambulance_bp.route('/start', methods=['POST'])
def start_ambulance():
    data = request.get_json()
    session_token = data.get('session_token')
    ambulance_id = data.get('ambulance_id', 'AMB001')
    
    if not validate_session(session_token):  # From app.py
        return jsonify({'success': False, 'message': 'Invalid session'}), 401
    
    conn = get_db_connection()
    driver_phone = conn.execute('SELECT phone FROM users WHERE role = "driver" AND phone IS NOT NULL LIMIT 1').fetchone()
    conn.close()
    
    if not driver_phone:
        return jsonify({'success': False, 'message': 'No driver account'}), 404
    
    driver_phone = driver_phone['phone']
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT OR REPLACE INTO ambulances (driver_phone, ambulance_id, status, last_update)
            VALUES (?, ?, 'active', ?)
        ''', (driver_phone, ambulance_id, datetime.now()))
        conn.commit()
        conn.close()
        notifications.console_alert(f"Ambulance {ambulance_id} started tracking", "🚑")
        return jsonify({'success': True, 'message': f'{ambulance_id} active', 'ambulance_id': ambulance_id}), 200
    except sqlite3.Error:
        conn.close()
        return jsonify({'success': False, 'message': 'DB error'}), 500

@ambulance_bp.route('/location', methods=['POST'])
def update_location():
    data = request.get_json()
    session_token = data.get('session_token')
    ambulance_id = data.get('ambulance_id')
    lat = data.get('lat', 0)
    lon = data.get('lon', 0)
    speed = data.get('speed', 0)
    
    if not ambulance_id:
        return jsonify({'success': False, 'message': 'Missing ambulance_id'}), 400
    
    conn = get_db_connection()
    # Update location
    eta = calculate_eta(5000)  # Placeholder, calc to nearest hospital later
    conn.execute('''
        UPDATE ambulances SET lat = ?, lon = ?, speed = ?, eta = ?, last_update = ? WHERE ambulance_id = ?
    ''', (lat, lon, speed, eta, datetime.now(), ambulance_id))
    conn.commit()
    
    # Check traffic signals geofence (300m)
    signals = conn.execute('SELECT * FROM traffic_signals').fetchall()
    for signal in signals:
        dist = haversine_distance(lat, lon, signal['lat'], signal['lon'])
        if dist < signal['radius']:
            old_state = signal['state']
            new_state = 'GREEN'
            conn.execute('UPDATE traffic_signals SET state = ?, controlled_by = ? WHERE id = ?', 
                        (new_state, ambulance_id, signal['id']))
            if old_state != new_state:
                signal_alert(ambulance_id, signal['name'], new_state)
                store_alert(ambulance_id, 'signal', f"Signal {signal['name']} -> GREEN")
    
    # Check hospitals (2km)
    hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    for hospital in hospitals:
        dist = haversine_distance(lat, lon, hospital['lat'], hospital['lon'])
        if dist < hospital['radius']:
            eta_min = calculate_eta(dist)
            hospital_notification(ambulance_id, hospital['name'], eta_min)
            store_alert(ambulance_id, 'hospital', f"Near {hospital['name']} ETA {eta_min}min")
    
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Location updated, checks done'}), 200

@ambulance_bp.route('/active', methods=['GET'])
def get_active_ambulances():
    conn = get_db_connection()
    active = conn.execute('SELECT * FROM ambulances WHERE status = "active" ORDER BY last_update DESC').fetchall()
    conn.close()
    return jsonify({'success': True, 'ambulances': [dict(a) for a in active]}), 200

