# 🚑 VibeCraft Ambulance Traffic Management System - Deployment Guide

## Overview
This project is a complete ambulance traffic signal preemption system with:
- **auth_backend**: Python Flask authentication API (port 5000)
- **ambulance-backend**: Node.js Socket.io real-time server (port 3000)  
- **project**: Static frontend (login + dashboard)

## 🚀 Deploy to Render

### Option 1: Using Render Blueprint (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit - VibeCraft Ambulance System"
   # Push to your GitHub repository
   ```

2. **Connect to Render**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` and show the services
   - Click "Apply" to deploy all 3 services

3. **Environment Variables (Optional)**
   For Twilio SMS functionality, set these in each service:
   ```
   TWILIO_ACCOUNT_SID=your_sid
   TWILIO_AUTH_TOKEN=your_token
   TWILIO_PHONE=+1234567890
   ```

### Option 2: Manual Deployment

#### 1. Deploy Auth Backend (Python)
```bash
# In Render dashboard:
- Name: vibecraft-auth
- Environment: Python
- Build Command: cd auth_backend && pip install -r requirements.txt
- Start Command: cd auth_backend && gunicorn app:app --bind 0.0.0.0:$PORT
- Region: US East (or closest to you)
```

#### 2. Deploy Ambulance Backend (Node.js)
```bash
# In Render dashboard:
- Name: vibecraft-ambulance
- Environment: Node
- Build Command: cd ambulance-backend && npm install
- Start Command: cd ambulance-backend && node server.js
- Region: US East
```

#### 3. Deploy Frontend (Static)
```bash
# In Render dashboard:
- Name: vibecraft-frontend
- Environment: Static
- Build Command: cd project && npm install && npm run build
- Static Publish Path: project/dist
# Note: Update index.html with actual backend URLs after deployment
```

## 🔧 Configuration

### Environment Variables
After deployment, update the frontend with the actual URLs:

**For login.html and index.html:**
```javascript
// Replace localhost URLs with your Render URLs
const API_BASE = 'https://your-auth-service.onrender.com/api';
const SOCKET_URL = 'https://your-ambulance-service.onrender.com';
```

### CORS Configuration
The Flask backend is already configured with CORS for all origins (`CORS(app)`), so it will work with your Render frontend.

## 🧪 Testing the Deployment

### Demo Users
After deployment, use these credentials:

| Role | Username | Password | Phone |
|------|----------|----------|-------|
| Admin | `admin` | `Admin@123` | +919999999999 |
| Driver | `driver` | `Driver@123` | +919999999998 |
| Demo | `demo` | `Demo@123` | +919999999997 |

### Flow to Test
1. Open frontend URL in browser
2. Login as `admin` / `Admin@123`
3. Open a second browser window (incognito)
4. Login as `driver` / `Driver@123`
5. Select a hospital destination
6. Click "Start Ambulance"
7. Watch signals turn GREEN as ambulance approaches
8. Admin dashboard will show real-time signal updates

## 📁 Project Structure
```
vibe-craft-hackathon/
├── auth_backend/
│   ├── app.py              # Flask application
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile           # Render deployment config
│   └── gunicorn.conf.py   # Gunicorn configuration
├── ambulance-backend/
│   ├── server.js          # Socket.io server
│   ├── package.json       # Node dependencies
│   └── Procfile          # Render deployment config
├── project/
│   ├── index.html         # Main dashboard
│   ├── login.html         # Authentication page
│   ├── dashboard.js       # Dashboard logic
│   ├── login.js          # Login logic
│   ├── config.js         # Environment configuration
│   ├── dashboard.css     # Dashboard styles
│   ├── login.css         # Login styles
│   └── package.json      # Frontend config
└── render.yaml           # Render Blueprint (all 3 services)
```

## ⚠️ Important Notes

### SQLite Database
The auth backend uses SQLite (`users.db`). On Render's free tier:
- **Data persists** during the lifetime of a service
- **Data resets** when the service restarts/redeploys
- For production, upgrade to Render's PostgreSQL add-on

### Free Tier Limitations
- Services sleep after 15 minutes of inactivity
- First request after sleep may take 30+ seconds
- For 24/7 availability, upgrade to paid plan

### Socket.IO Considerations
- WebSocket connections work on Render
- May need sticky sessions for load-balanced deployments
- Free tier should work fine for this prototype

## 🔒 Security Recommendations

1. **Change default passwords** before production deployment
2. **Add JWT authentication** for enhanced security
3. **Use HTTPS** (Render provides this automatically)
4. **Environment variables** for all secrets
5. **Input validation** on all API endpoints

## 📞 Support

For issues:
1. Check Render service logs
2. Verify environment variables
3. Test locally first with `python app.py` and `node server.js`
4. Check browser console for frontend errors

## 🎯 Quick Start Commands

```bash
# Local development
# Terminal 1 - Auth backend
cd auth_backend && python app.py

# Terminal 2 - Ambulance backend  
cd ambulance-backend && node server.js

# Terminal 3 - Frontend (optional, can open directly)
cd project && npx serve .
```

Then open:
- Frontend: http://localhost:3000 (or 5000 depending on serve)
- Auth API: http://localhost:5000
- Socket: http://localhost:3000

