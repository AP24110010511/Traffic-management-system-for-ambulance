# Traffic Management System Extension - Implementation TODO

## Status Legend
- [ ] **TODO** Not started
- [>] **IN PROGRESS** Working
- [x] **DONE** Completed & tested

## 1. Dependencies & Setup [x DONE]
- [x] Update auth_backend/requirements.txt (add geopy)
- [x] Install deps: `pip install -r auth_backend/requirements.txt`
- [x] Verify SQLite users.db exists

## 2. Core App Refactor [x DONE]
- [x] Create utils/ dir + distance.py (haversine), notifications.py
- [x] Refactor app.py: Extract auth to auth/blueprint.py, extend init_db() with new tables
- [x] Register blueprints in app.py (ambulance, traffic, hospital, admin)

## 3. New Modules/Blueprints [x DONE]
- [x] ambulance/blueprint.py: start, location update, active list
- [ ] traffic/blueprint.py: signals state, auto-green logic
- [ ] hospital/blueprint.py: nearby detection + alerts
- [ ] admin/blueprint.py: dashboard API

## 4. Features Implementation [ ]
- [ ] Ambulance OTP login + session → start tracking
- [ ] Live GPS update → geofence signals (300m GREEN)
- [ ] Hospital proximity (2km) → ETA calc + notify
- [ ] Admin dashboard data (live amb/signals/alerts)

## 5. Testing [ ]
- [ ] Manual: curl login → start amb → update GPS → check signals/alerts
- [ ] Verify console alerts, DB updates
- [ ] Frontend integration ready (JSON APIs)

## 6. Demo & Deploy [ ]
- [ ] Run `python app.py` + Postman tests
- [ ] Update root Procfile for gunicorn if needed

**Next Step**: Update requirements.txt → pip install → proceed to utils/**

