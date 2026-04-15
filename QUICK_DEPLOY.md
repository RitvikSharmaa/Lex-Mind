# ⚡ Quick Deploy: Render + Netlify

## 🎯 Goal
Deploy your LexMind AI app for FREE in 25 minutes!

---

## 📦 Part 1: Backend on Render (15 min)

### 1. Sign Up
```
→ Go to https://render.com/
→ Click "Get Started for Free"
→ Sign up with GitHub
```

### 2. Create Web Service
```
→ Click "New +" → "Web Service"
→ Connect your GitHub repo
```

### 3. Configure
```
Name: lexmind-backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python backend_api.py
Instance: Free
```

### 4. Add Environment Variables
```
OPENROUTER_API_KEY = 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
FLASK_ENV = production
FLASK_DEBUG = False
```

### 5. Deploy
```
→ Click "Create Web Service"
→ Wait 10-15 minutes ☕
→ Look for "Live" status (green)
→ Copy your URL: https://lexmind-backend.onrender.com
```

### 6. Test
```
Open: https://your-backend.onrender.com/api/health
Should see: {"status": "healthy", "models_loaded": true}
```

---

## 🎨 Part 2: Frontend on Netlify (10 min)

### 1. Update Config
```bash
# Edit frontend/.env.production
VITE_API_URL=https://lexmind-backend.onrender.com
# (Use YOUR Render URL!)

# Update code
python update_api_urls.py
```

### 2. Build
```bash
cd frontend
npm install
npm run build
```

### 3. Deploy

**Option A: Drag & Drop (Easiest)**
```
→ Go to https://www.netlify.com/
→ Sign up with GitHub
→ Drag frontend/dist folder to Netlify
→ Done! Copy your URL
```

**Option B: CLI**
```bash
npm install -g netlify-cli
netlify login
cd frontend
netlify deploy --prod
# Follow prompts, publish directory: dist
```

### 4. Update CORS
```
→ Go back to Render dashboard
→ Click your service → Environment tab
→ Add variable:
   FRONTEND_URL = https://your-app.netlify.app
→ Save (auto-redeploys in 2-3 min)
```

---

## ✅ Test Your App

```
1. Open: https://your-app.netlify.app
2. Try Case Retrieval: Search "theft"
3. Try Summarization: Select case C1
4. Try Chat: Ask "What is punishment for theft?"
5. Check Analytics tab
```

---

## 🎉 Done!

**Your URLs:**
- Backend: https://lexmind-backend.onrender.com
- Frontend: https://your-app.netlify.app

**Cost:** $0
**Time:** 25 minutes

---

## 💡 Pro Tip: Keep Backend Awake

Render spins down after 15 min. Keep it awake:

```
1. Go to https://uptimerobot.com/
2. Sign up (free)
3. Add monitor:
   - URL: https://your-backend.onrender.com/api/health
   - Interval: 14 minutes
4. Done! Now it stays awake 24/7
```

---

## 🐛 Common Issues

**Backend taking 30-60s to respond?**
→ Normal after spin-down. Use UptimeRobot.

**CORS errors?**
→ Make sure FRONTEND_URL is set in Render.

**Can't connect to backend?**
→ Check if backend URL in .env.production is correct.

**Build failed?**
→ Check Render logs for errors.

---

## 📚 Full Guide

See `RENDER_NETLIFY_GUIDE.md` for detailed instructions!

---

**Need help?** Check the troubleshooting section in the full guide.
