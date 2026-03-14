"""
Traffic Signal Blueprint
GET /api/traffic/signals → current states
Logic in ambulance/location update (auto GREEN on approach)
"""

from flask import Blueprint, jsonify
import sys
sys.path.append('.')
from utils.db import get_db_connection

traffic_bp = Blueprint('traffic', __name__, url_prefix='/api/traffic')

@traffic_bp.route('/signals', methods=['GET'])
def get_signals():
    conn = get_db_connection()
    signals = conn.execute('SELECT * FROM traffic_signals ORDER BY id').fetchall()
    conn.close()
    return jsonify({'success': True, 'signals': [dict(s) for s in signals]}), 200

