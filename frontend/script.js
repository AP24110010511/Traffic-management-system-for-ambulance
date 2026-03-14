const API_BASE = 'http://127.0.0.1:5000/api';
let currentRole = 'driver';
let currentPhone = '';
let currentToken = '';
let map, ambulanceMarker, signalMarkers = {};

// Navigation
function goToLanding() {
    window.location.hash = 'landing';
    showSection('landing');
}

function goToLogin(role) {
    currentRole = role;
    document.getElementById('login-title').textContent = role === 'driver' ? 'Driver Portal' : 'Admin Dashboard';
    window.location.hash = 'login';
    showSection('login');
    setTimeout(() => document.getElementById('phone').focus(), 300);
}

function logout() {
    currentPhone = '';
    currentToken = '';
    goToLanding();
}

function showSection(sectionId) {
    document.querySelectorAll('.page, .hero, .features, .login-section, .dashboard-section').forEach(section => {
        section.classList.remove('active');
        section.style.display = 'none';
    });
    const target = document.getElementById(sectionId) || document.querySelector(`[id*="${sectionId}"]`);
    if (target) {
        target.style.display = 'block';
        target.classList.add('active');
        if (sectionId === 'dashboard') setTimeout(initDashboard, 300);
    }
}

// OTP Flow
function sendOTP() {
    const phone = document.getElementById('phone').value.trim();
    if (!phone || phone.length < 10) return showAlert('Enter valid phone (10 digits)', 'error');

    const btn = document.getElementById('send-otp-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';

    fetch(`${API_BASE}/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone, role: currentRole })
        })
        .then(res => res.json())
        .then(data => {
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-sms"></i> Send OTP';

            if (data.success) {
                currentPhone = data.data.phone;
                document.getElementById('otp-section').classList.remove('hidden');
                showAlert(`OTP sent to ${data.data.phone.slice(-4)}! Check terminal`, 'success');
            } else {
                showAlert(data.message, 'error');
            }
        })
        .catch(() => {
            btn.innerHTML = '<i class="fas fa-sms"></i> Send OTP';
            showAlert('Backend down? cd backend && python3 app.py', 'error');
        });
}

function verifyOTP() {
    const otp = document.getElementById('otp').value;
    if (otp.length !== 4) return showAlert('4-digit OTP required', 'error');

    fetch(`${API_BASE}/verify-otp`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ phone: currentPhone, otp })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                currentToken = data.data.session_token;
                goToDashboard();
            } else {
                showAlert(data.message, 'error');
                document.getElementById('otp').value = '';
                document.getElementById('otp').focus();
            }
        })
        .catch(() => showAlert('Verification failed', 'error'));
}

function goToDashboard() {
    document.getElementById('dashboard-title').textContent = `${currentRole.charAt(0).toUpperCase() + currentRole.slice(1)} Dashboard - Ambi`;
    window.location.hash = 'dashboard';
    showSection('dashboard');
}

// Dashboard
function initDashboard() {
    initMap();
    refreshStatus();
}

function initMap() {
    map = L.map('map').setView([17.3850, 78.4860], 16);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    ambulanceMarker = L.marker([17.3850, 78.4860], {
        icon: L.divIcon({ className: 'custom-icon', html: '<i class="fas fa-ambulance" style="font-size:24px;color:#D4AF37"></i>', iconSize: [36, 36] })
    }).addTo(map);

    fetch(`${API_BASE}/signal-status`).then(res => res.json()).then(data => {
        if (data.success) data.data.forEach(s => {
            const iconHtml = `<i class="fas fa-traffic-light" style="color:${s.state==='GREEN' ? '#22c55e' : '#666'};font-size:20px"></i>`;
            const icon = L.divIcon({ className: 'signal-icon', html: iconHtml, iconSize: [30, 30] });
            signalMarkers[s.id] = L.marker([s.lat, s.lon], { icon }).addTo(map).bindPopup(`Signal ${s.name}`);
        });
    });
}

function updateLocation() {
    const lat = parseFloat(document.getElementById('lat').value);
    const lon = parseFloat(document.getElementById('lon').value);
    const hospital = document.getElementById('hospital').value;

    ambulanceMarker.setLatLng([lat, lon]);
    map.setView([lat, lon], 17);

    fetch(`${API_BASE}/update-location`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat, lon, id: 'AMB001', hospital, speed: 50 })
    }).then(res => res.json()).then(data => {
        if (data.success) {
            document.getElementById('eta-display').innerHTML = `<i class="fas fa-stopwatch"></i><div>${data.data.eta} min</div>`;
            if (data.data.green_signals ? .length) {
                showAlert(`✅ ${data.data.green_signals.join(', ')} GREEN!`);
                refreshStatus();
            }
        } else {
            showAlert(data.message, 'error');
        }
    });
}

function sendHospitalAlert() {
    fetch(`${API_BASE}/hospital-alert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ambulance_id: 'AMB001', hospital: document.getElementById('hospital').value, eta: 4.5 })
    }).then(res => res.json()).then(data => {
        showAlert(data.success ? '🚨 Hospital notified' : data.message, data.success ? 'success' : 'error');
    });
}

function refreshStatus() {
    Promise.all([
        fetch(`${API_BASE}/ambulance-status`).then(r => r.json()),
        fetch(`${API_BASE}/signal-status`).then(r => r.json()),
        fetch(`${API_BASE}/eta`).then(r => r.json())
    ]).then(([amb, sig, eta]) => {
        if (amb.success && amb.data.length) {
            const a = amb.data[0];
            document.getElementById('amb-status').innerHTML = `<i class="fas fa-ambulance"></i><div>${a.id}<br>${a.status}</div>`;
        }
        if (sig.success) document.getElementById('sig-status').innerHTML = `<i class="fas fa-traffic-light"></i><div>${sig.data.filter(s=>s.state==='GREEN').length}/${sig.data.length} GREEN</div>`;
        if (eta.success) document.getElementById('eta-display').innerHTML = `<i class="fas fa-stopwatch"></i><div>${eta.data.eta_minutes || 0} min</div>`;
    }).catch(() => {});
}

function showAlert(msg, type = 'success') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = msg;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 4000);
}

// Scroll animations
function revealOnScroll() {
    document.querySelectorAll('.feature-card, .stat').forEach(el => {
        const rect = el.getBoundingClientRect();
        if (rect.top < window.innerHeight * 0.8) el.classList.add('active');
    });
}

window.addEventListener('scroll', revealOnScroll);
window.addEventListener('load', revealOnScroll);

// Hash navigation
window.addEventListener('hashchange', () => {
    const hash = location.hash.slice(1) || 'landing';
    if (hash === 'login') goToLogin(currentRole);
    else if (hash === 'dashboard') showSection('dashboard');
    else goToLanding();
});

// Init
document.addEventListener('DOMContentLoaded', () => {
    if (!location.hash) goToLanding();
});