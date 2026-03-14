"""
Admin Dashboard API
GET /api/admin/dashboard → all data (amb, signals, hospitals, alerts)
"""

from flask import Blueprint, jsonify
import sys
sys.path.append('.')
from utils.db import get_db_connection

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard', methods=['GET'])
def dashboard():
    conn = get_db_connection()
    ambulances = conn.execute('SELECT * FROM ambulances WHERE status = "active"').fetchall()
    signals = conn.execute('SELECT * FROM traffic_signals').fetchall()
    hospitals = conn.execute('SELECT * FROM hospitals').fetchall()
    alerts = conn.execute('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT 10').fetchall()
    conn.close()
    return jsonify({
        'success': True,
        'data': {
            'ambulances': [dict(a) for a in ambulances],
            'signals': [dict(s) for s in signals],
            'hospitals': [dict(h) for h in hospitals],
            'recent_alerts': [dict(al) for al in alerts]
        }
    }), 200

