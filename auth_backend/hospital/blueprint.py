"""
Hospital Blueprint
GET /api/hospital/all → list
"""

from flask import Blueprint, jsonify
import sys
sys.path.append('.')
from utils.db import get_db_connection

hospital_bp = Blueprint('hospital', __name__, url_prefix='/api/hospital')

@hospital_bp.route('/all', methods=['GET'])
def get_hospitals():
    conn = get_db_connection()
    hospitals = conn.execute('SELECT * FROM hospitals ORDER BY id').fetchall()
    conn.close()
    return jsonify({'success': True, 'hospitals': [dict(h) for h in hospitals]}), 200

