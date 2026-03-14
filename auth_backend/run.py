#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, init_db, register_blueprints

if __name__ == '__main__':
    init_db()
    register_blueprints()
    app.run(host='0.0.0.0', port=5000, debug=True)

