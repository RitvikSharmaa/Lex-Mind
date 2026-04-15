# 🚀 Deployment Guide

## ⚠️ IMPORTANT: Don't Deploy Everything on Vercel!

Your app has large ML models that won't work on Vercel's free tier. Use this strategy instead:

## ✅ Recommended: Railway (Backend) + Vercel (Frontend)

### Step 1: Deploy Backend on Railway (5 minutes)

1. **Sign up for Railway**
   - Go to https://railway.app/
   - Click "Login with GitHub"
   - Authorize Railway

2. **Create New Project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository
   - Railway will auto-detect it's a Python app

3. **Add Environment Variable**
   - Click on your project
   - Go to "Variables" tab
   - Click "New Variable"
   - Add:
     ```
     OPENROUTER_API_KEY=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
     ```
   - Click "Add"

4. **Wait for Deployment** (5-10 minutes)
   - Railway will install dependencies
   - Load your models
   - Start the Flask server

5. **Get Your URL**
   - Click "Settings" tab
   - Under "Domains", click "Generate Domain"
   - Copy the URL (e.g., `https://your-app.railway.app`)

### Step 2: Update Frontend Configuration

1. **Edit `frontend/.env.production`**
   ```bash
   VITE_API_URL=https://your-app.railway.app
   ```
   Replace `your-app.railway.app` with your actual Railway URL

2. **Update App.tsx to use config**
   
   The frontend needs to use the API_URL from config instead of hardcoded localhost.
   
   I'll create a script to do this automatically:

### Step 3: Deploy Frontend on Vercel (2 minutes)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend
   vercel --prod
   ```

4. **Follow Prompts**
   - Set up and deploy? Yes
   - Which scope? Your account
   - Link to existing project? No
   - Project name? lexmind-ai (or your choice)
   - Directory? ./
   - Override settings? No

5. **Done!**
   - Vercel will give you a URL like `https://lexmind-ai.vercel.app`

### Step 4: Update CORS in Backend

After deploying, update your backend CORS settings:

1. Go to Railway dashboard
2. Click on your project
3. Go to "Variables"
4. Add new variable:
   ```
   FRONTEND_URL=https://your-vercel-app.vercel.app
   ```

Or manually edit `backend_api.py` on Railway:
```python
CORS(app, origins=[
    'http://localhost:3000',
    'https://your-vercel-app.vercel.app'
])
```

## 🎉 You're Done!

Your app is now live:
- **Backend**: https://your-app.railway.app
- **Frontend**: https://your-vercel-app.vercel.app

## 💰 Cost

- **Railway**: Free tier (500 hours/month) - More than enough!
- **Vercel**: Free tier (unlimited for frontend)
- **Total**: $0/month 🎉

## 🔧 Alternative: Deploy Frontend Only on Vercel

If you want to keep the backend running locally:

1. **Keep backend running locally**
   ```bash
   python backend_api.py
   ```

2. **Use ngrok to expose it**
   ```bash
   ngrok http 5000
   ```

3. **Update frontend .env.production**
   ```
   VITE_API_URL=https://your-ngrok-url.ngrok.io
   ```

4. **Deploy frontend to Vercel**
   ```bash
   cd frontend
   vercel --prod
   ```

## 📝 Quick Commands

```bash
# Deploy backend to Railway
railway login
railway init
railway up
railway variables set OPENROUTER_API_KEY=your_key

# Deploy frontend to Vercel
cd frontend
vercel --prod
```

## 🆘 Troubleshooting

### Backend Issues on Railway

**Problem**: Models not loading
- **Solution**: Railway has enough memory, just wait 5-10 minutes for first deployment

**Problem**: App crashes
- **Solution**: Check logs in Railway dashboard → "Deployments" → Click latest → "View Logs"

**Problem**: API key not working
- **Solution**: Double-check the environment variable in Railway dashboard

### Frontend Issues on Vercel

**Problem**: Can't connect to backend
- **Solution**: Check if `VITE_API_URL` is set correctly in `.env.production`

**Problem**: CORS errors
- **Solution**: Add your Vercel URL to CORS origins in `backend_api.py`

**Problem**: Build fails
- **Solution**: Make sure all dependencies are in `package.json`

## 📚 Resources

- Railway Docs: https://docs.railway.app/
- Vercel Docs: https://vercel.com/docs
- Railway Discord: https://discord.gg/railway (for help)

## 🎯 Next Steps After Deployment

1. Test all features on production
2. Share your app URL!
3. Monitor Railway usage (free tier has limits)
4. Consider upgrading if you need more resources

---

**Need help?** Check the Railway/Vercel documentation or open an issue on GitHub.
