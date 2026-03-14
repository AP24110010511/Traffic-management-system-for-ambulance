"""
Notification system simulation (console + DB alert store).
For dashboard alerts and console logs.
Email/Twilio extension possible.
"""

import datetime

def console_alert(msg: str, emoji: str = "🚨"):
    """Print formatted console alert (visible in terminal)."""
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"\n{emoji} [{timestamp}] TRAFFIC ALERT: {msg}\n")

def hospital_notification(ambulance_id: str, hospital: str, eta_min: float):
    """Hospital proximity alert."""
    msg = f"Ambulance {ambulance_id} approaching {hospital} | ETA: {eta_min} min"
    console_alert(msg, "🏥")

def signal_alert(ambulance_id: str, signal_name: str, action: str):
    """Traffic signal change alert."""
    msg = f"Signal '{signal_name}' turned {action} for Ambulance {ambulance_id}"
    console_alert(msg, "🟢")

# Placeholder for DB store (used by admin dashboard)
def store_alert(ambulance_id: str, alert_type: str, message: str):
    """
    Store for persistence (admin view).
    In real: DB insert; here console sim.
    """
    print(f"[DB] Stored alert: {ambulance_id} | {alert_type} | {message}")

if __name__ == "__main__":
    print("🔔 Notification Demo")
    hospital_notification("AMB001", "Apollo Hospital", 5.2)
    signal_alert("AMB001", "Signal-1 (MG Road)", "GREEN")

