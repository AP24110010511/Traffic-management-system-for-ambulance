# 🚑 VibeCraft Ambulance Traffic Management System - Deployment Guide

## Project Structure
```
ambulance-traffic-management/
│
├── app.py              # Flask application (ROOT)
├── requirements.txt    # Python dependencies (ROOT)
├── runtime.txt         # Python version (ROOT)
│
├── ambulance-backend/  # Node.js Socket.io server
├── auth_backend/       # (keep for local dev only)
├── project/           # Frontend (HTML/CSS/JS)
└── users.db           # SQLite database (auto-created)
```

## 🚀 Deploy to Render

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push
```

### Step 2: Connect to Render Blueprint
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Blueprint"
3. Connect your GitHub repo: `AP24110010511/Traffic-management-system-for-ambulance`
4. Render will detect `render.yaml` automatically
5. Click "Apply" to deploy all 3 services

### Step 3: Configure Services

#### Auth Service (Python)
- **Name**: vibecraft-auth
- **Environment**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`
- **Region**: US East

#### Ambulance Service (Node.js)
- **Name**: vibecraft-ambulance
- **Environment**: Node
- **Build Command**: `cd ambulance-backend && npm install`
- **Start Command**: `cd ambulance-backend && node server.js`
- **Region**: US East

#### Frontend Service (Static)
- **Name**: vibecraft-frontend
- **Environment**: Static
- **Build Command**: `cd project && npm install && npm run build`
- **Static Publish Path**: `project/dist`
- **Region**: US East

## 🧪 Testing

### Demo Credentials
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `Admin@123` |
| Driver | `driver` | `Driver@123` |

### Local Testing
```bash
# Terminal 1 - Auth (Python)
python3 app.py

# Terminal 2 - Ambulance (Node.js)
cd ambulance-backend && node server.js

# Terminal 3 - Frontend
cd project && python3 -m http.server 8080
```

Open http://localhost:8080 in your browser.

## 🔐 Environment Variables (Optional)

For Twilio SMS functionality, set in Render dashboard:
```
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE=+1234567890
```

## ⚠️ Important Notes

1. **SQLite Database**: Data resets on redeploy. For persistence, upgrade to Render PostgreSQL.

2. **Free Tier**: Services sleep after 15min inactivity. First request may take 30+ seconds.

3. **Frontend URLs**: After deployment, update `project/config.js` with actual Render URLs.

## 📁 Services

| Service | Description | URL Pattern |
|---------|-------------|-------------|
| Auth API | Flask login/register | https://vibecraft-auth.onrender.com |
| Socket.IO | Real-time updates | https://vibecraft-ambulance.onrender.com |
| Frontend | Dashboard UI | https://vibecraft-frontend.onrender.com |

