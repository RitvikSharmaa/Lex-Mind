# ✅ Vercel Deployment Checklist

## What You Need to Do:

### 🚫 DON'T Deploy Backend on Vercel
Your backend has large ML models that won't work on Vercel's free tier.

### ✅ DO This Instead:

## Step 1: Deploy Backend on Railway (10 minutes)

- [ ] Go to https://railway.app/
- [ ] Sign up with GitHub
- [ ] Click "New Project" → "Deploy from GitHub repo"
- [ ] Select your repository
- [ ] Wait for auto-detection (Python app)
- [ ] Go to "Variables" tab
- [ ] Add variable: `OPENROUTER_API_KEY` = `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`
- [ ] Wait 5-10 minutes for deployment
- [ ] Go to "Settings" → "Generate Domain"
- [ ] Copy your Railway URL (e.g., `https://lexmind-ai.railway.app`)

## Step 2: Update Frontend (2 minutes)

- [ ] Open `frontend/.env.production`
- [ ] Replace `your-app.railway.app` with your actual Railway URL
- [ ] Run: `python update_api_urls.py` (updates App.tsx automatically)

## Step 3: Deploy Frontend on Vercel (5 minutes)

- [ ] Install Vercel CLI: `npm install -g vercel`
- [ ] Login: `vercel login`
- [ ] Go to frontend: `cd frontend`
- [ ] Build: `npm run build`
- [ ] Deploy: `vercel --prod`
- [ ] Follow prompts (accept defaults)
- [ ] Copy your Vercel URL (e.g., `https://lexmind-ai.vercel.app`)

## Step 4: Update CORS (2 minutes)

- [ ] Go back to Railway dashboard
- [ ] Click your project → "Variables"
- [ ] Add: `FRONTEND_URL` = `https://your-vercel-app.vercel.app`
- [ ] Railway will auto-redeploy

## 🎉 Done!

Your app is live at:
- Backend: https://your-app.railway.app
- Frontend: https://your-vercel-app.vercel.app

## 💡 Quick Commands

```bash
# Update frontend API URLs
python update_api_urls.py

# Deploy frontend to Vercel
cd frontend
npm run build
vercel --prod
```

## 🆘 If Something Goes Wrong

1. **Backend not loading**: Wait 10 minutes, Railway needs time to load models
2. **CORS errors**: Make sure you added FRONTEND_URL to Railway variables
3. **API connection failed**: Check if Railway URL is correct in `.env.production`
4. **Build fails**: Run `npm install` in frontend folder

## 📞 Need Help?

- Railway Discord: https://discord.gg/railway
- Vercel Discord: https://discord.gg/vercel
- Check logs in Railway dashboard

---

**Total Time**: ~20 minutes
**Total Cost**: $0 (both free tiers)
