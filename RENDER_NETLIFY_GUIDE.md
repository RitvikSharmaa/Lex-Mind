# 🚀 Complete Guide: Render (Backend) + Netlify (Frontend)

## Why This Combo?
- ✅ 100% FREE forever
- ✅ No credit card required
- ✅ Supports your large ML models
- ✅ Easy to set up
- ✅ Professional URLs
- ✅ Automatic HTTPS

---

## 📋 What You'll Get

After deployment:
- **Backend**: `https://lexmind-backend.onrender.com`
- **Frontend**: `https://lexmind-ai.netlify.app`
- **Total Time**: 25 minutes
- **Total Cost**: $0

---

# Part 1: Deploy Backend on Render (15 minutes)

## Step 1: Sign Up for Render

1. Go to https://render.com/
2. Click **"Get Started for Free"**
3. Sign up with **GitHub** (easiest option)
4. Authorize Render to access your GitHub

## Step 2: Create Web Service

1. Click **"New +"** button (top right)
2. Select **"Web Service"**
3. Click **"Connect a repository"**
4. Find your project repo and click **"Connect"**

## Step 3: Configure Your Service

Fill in these settings:

### Basic Settings:
- **Name**: `lexmind-backend` (or any name you like)
- **Region**: Choose closest to you (e.g., Oregon, Frankfurt)
- **Branch**: `main` (or `master`)
- **Root Directory**: Leave empty
- **Runtime**: **Python 3**

### Build Settings:
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```

- **Start Command**:
  ```bash
  python backend_api.py
  ```

### Instance Type:
- Select **"Free"** (should be selected by default)

## Step 4: Add Environment Variables

Scroll down to **"Environment Variables"** section:

1. Click **"Add Environment Variable"**
2. Add these variables:

| Key | Value |
|-----|-------|
| `OPENROUTER_API_KEY` | `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` |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `False` |

## Step 5: Create Web Service

1. Click **"Create Web Service"** button at the bottom
2. Render will start building your app
3. **Wait 10-15 minutes** (first deploy takes time to download models)

### What's Happening:
- Installing Python dependencies
- Downloading ML models (MPNet, BART, BERT)
- Loading FAISS index
- Starting Flask server

### Monitor Progress:
- Watch the **"Logs"** tab to see progress
- Look for: `Models loaded successfully!`
- Then: `Running on http://0.0.0.0:5000`

## Step 6: Get Your Backend URL

1. Once deployed, you'll see **"Live"** status (green)
2. Your URL will be at the top: `https://lexmind-backend.onrender.com`
3. **Copy this URL** - you'll need it for the frontend!

### Test Your Backend:

Open in browser:
```
https://lexmind-backend.onrender.com/api/health
```

You should see:
```json
{"status": "healthy", "models_loaded": true}
```

---

# Part 2: Deploy Frontend on Netlify (10 minutes)

## Step 1: Update Frontend Configuration

### 1.1: Edit Environment File

Open `frontend/.env.production` and update:

```bash
VITE_API_URL=https://lexmind-backend.onrender.com
```

Replace `lexmind-backend.onrender.com` with YOUR actual Render URL!

### 1.2: Update API URLs in Code

Run this script to automatically update all API calls:

```bash
python update_api_urls.py
```

This will update `frontend/src/App.tsx` to use the environment variable.

## Step 2: Build Frontend

```bash
cd frontend
npm install
npm run build
```

This creates a `dist/` folder with your production build.

## Step 3: Sign Up for Netlify

1. Go to https://www.netlify.com/
2. Click **"Sign up"**
3. Choose **"Sign up with GitHub"**
4. Authorize Netlify

## Step 4: Deploy to Netlify

### Option A: Drag & Drop (Easiest)

1. In Netlify dashboard, scroll down to **"Want to deploy a new site without connecting to Git?"**
2. Drag the `frontend/dist` folder into the box
3. Wait 30 seconds
4. Done! You'll get a URL like `https://random-name-123.netlify.app`

### Option B: Using CLI (Recommended)

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login
# (Opens browser, click "Authorize")

# Deploy
cd frontend
netlify deploy --prod

# Follow prompts:
# ? Create & configure a new site: Yes
# ? Team: Your team
# ? Site name: lexmind-ai (or leave blank for random)
# ? Publish directory: dist

# Done! Copy your URL
```

## Step 5: Get Your Frontend URL

After deployment, you'll get a URL like:
- `https://lexmind-ai.netlify.app` (if you chose a name)
- `https://random-name-123.netlify.app` (if random)

**Copy this URL!**

## Step 6: Update CORS in Backend

Go back to Render:

1. Open your Render dashboard
2. Click on your **lexmind-backend** service
3. Go to **"Environment"** tab
4. Click **"Add Environment Variable"**
5. Add:
   - **Key**: `FRONTEND_URL`
   - **Value**: `https://your-app.netlify.app` (your actual Netlify URL)
6. Click **"Save Changes"**

Render will automatically redeploy (takes 2-3 minutes).

---

# Part 3: Test Your Deployed App (5 minutes)

## Step 1: Open Your App

Go to your Netlify URL: `https://your-app.netlify.app`

## Step 2: Test Each Feature

### Test 1: Case Retrieval
1. Click **"Case Retrieval"** tab
2. Search for: `cheque dishonour`
3. Should return 5 results in <2 seconds
4. ✅ If you see results, it works!

### Test 2: Summarization
1. Click **"Summarization"** tab
2. Type `C1` in search box
3. Select a case
4. Click **"Generate Summary"**
5. Wait 30-60 seconds
6. ✅ If you see a summary, it works!

### Test 3: Chat (RAG)
1. Click **"Q&A"** tab
2. Ask: `What is the punishment for theft?`
3. Wait 5-10 seconds
4. ✅ If you see an AI response with retrieved documents, it works!

### Test 4: Analytics
1. Click **"Analytics"** tab
2. ✅ Should show document statistics

---

# 🎉 You're Live!

Your app is now deployed and accessible worldwide!

- **Backend**: https://lexmind-backend.onrender.com
- **Frontend**: https://your-app.netlify.app

---

# ⚠️ Important: Render Free Tier Limitations

## Spin-Down After Inactivity

Render's free tier **spins down after 15 minutes** of no requests.

### What This Means:
- If no one uses your app for 15 minutes, Render stops the server
- Next request will take **30-60 seconds** (models need to reload)
- After that, it's fast again

### Solution: Keep It Awake (Optional)

Use **UptimeRobot** to ping your app every 14 minutes:

1. Go to https://uptimerobot.com/
2. Sign up (free)
3. Click **"Add New Monitor"**
4. Settings:
   - **Monitor Type**: HTTP(s)
   - **Friendly Name**: LexMind Backend
   - **URL**: `https://lexmind-backend.onrender.com/api/health`
   - **Monitoring Interval**: 14 minutes
5. Click **"Create Monitor"**

Now your app stays awake 24/7! 🎉

---

# 🔧 Updating Your App

## Update Backend:

1. Push changes to GitHub
2. Render auto-deploys (if you connected GitHub)
3. Or manually: Click **"Manual Deploy"** → **"Deploy latest commit"**

## Update Frontend:

```bash
cd frontend
npm run build
netlify deploy --prod
```

---

# 🐛 Troubleshooting

## Backend Issues

### Problem: "Application failed to respond"
**Solution**: Wait 10-15 minutes for first deploy. Models are large!

### Problem: "Build failed"
**Solution**: 
- Check logs in Render dashboard
- Make sure `requirements.txt` is in root directory
- Verify Python version compatibility

### Problem: Backend is slow (30-60s response)
**Solution**: This is normal after spin-down. Use UptimeRobot to keep it awake.

### Problem: "ModuleNotFoundError"
**Solution**: 
- Check if all dependencies are in `requirements.txt`
- Redeploy: Click "Manual Deploy" → "Clear build cache & deploy"

## Frontend Issues

### Problem: "Failed to fetch" or CORS errors
**Solution**: 
- Make sure `FRONTEND_URL` is set in Render environment variables
- Check if backend URL in `.env.production` is correct
- Wait 2-3 minutes after updating CORS for Render to redeploy

### Problem: Blank page
**Solution**:
- Open browser console (F12)
- Check for errors
- Make sure `dist/` folder was deployed
- Verify API URL is correct

### Problem: "Cannot connect to backend"
**Solution**:
- Test backend directly: `https://your-backend.onrender.com/api/health`
- If backend works, check CORS settings
- Make sure you ran `python update_api_urls.py`

## Chat Not Working

### Problem: "Error: HTTP error! status: 500"
**Solution**:
- Check Render logs for errors
- Verify `OPENROUTER_API_KEY` is set correctly
- Test API key: Try a simple question

### Problem: Chat is very slow
**Solution**:
- First request after spin-down takes 30-60s (normal)
- Subsequent requests should be 5-10s
- Use UptimeRobot to prevent spin-down

---

# 📊 Monitoring Your App

## Render Dashboard:

- **Logs**: See real-time server logs
- **Metrics**: CPU, Memory usage
- **Events**: Deployment history
- **Settings**: Update environment variables

## Netlify Dashboard:

- **Deploys**: Deployment history
- **Functions**: (not used in your app)
- **Analytics**: Visitor stats (paid feature)
- **Domain**: Custom domain settings

---

# 💰 Costs & Limits

## Render Free Tier:

- **750 hours/month** (about 25 hours/day)
- **512MB RAM** (should be enough)
- **Spins down after 15 min** inactivity
- **Unlimited bandwidth**
- **Automatic HTTPS**

## Netlify Free Tier:

- **100GB bandwidth/month**
- **300 build minutes/month**
- **Unlimited sites**
- **Automatic HTTPS**
- **Custom domains** (free)

## Total Cost: $0/month 🎉

---

# 🚀 Next Steps

## 1. Custom Domain (Optional)

### For Frontend (Netlify):
1. Buy domain (e.g., Namecheap, Google Domains)
2. In Netlify: **Domain settings** → **Add custom domain**
3. Update DNS records
4. Done! (Free HTTPS included)

### For Backend (Render):
1. In Render: **Settings** → **Custom Domain**
2. Add your domain
3. Update DNS records
4. Done!

## 2. Monitor Usage

- Check Render dashboard for hours used
- Check Netlify for bandwidth usage
- Set up UptimeRobot to prevent spin-down

## 3. Share Your App!

Your app is live! Share the URL:
- `https://your-app.netlify.app`

---

# 📚 Useful Commands

```bash
# Update frontend
cd frontend
npm run build
netlify deploy --prod

# Check backend logs
# (Use Render dashboard → Logs tab)

# Test backend health
curl https://your-backend.onrender.com/api/health

# Test API endpoint
curl -X POST https://your-backend.onrender.com/api/retrieve \
  -H "Content-Type: application/json" \
  -d '{"query": "theft", "k": 5}'
```

---

# 🆘 Need Help?

- **Render Docs**: https://render.com/docs
- **Netlify Docs**: https://docs.netlify.com/
- **Render Community**: https://community.render.com/
- **Netlify Community**: https://answers.netlify.com/

---

# ✅ Deployment Checklist

## Backend (Render):
- [ ] Signed up for Render
- [ ] Created Web Service
- [ ] Connected GitHub repo
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `python backend_api.py`
- [ ] Added `OPENROUTER_API_KEY` environment variable
- [ ] Waited 10-15 minutes for deployment
- [ ] Tested `/api/health` endpoint
- [ ] Copied backend URL

## Frontend (Netlify):
- [ ] Updated `frontend/.env.production` with Render URL
- [ ] Ran `python update_api_urls.py`
- [ ] Built frontend: `npm run build`
- [ ] Signed up for Netlify
- [ ] Deployed `dist/` folder
- [ ] Copied frontend URL
- [ ] Added `FRONTEND_URL` to Render environment variables
- [ ] Waited for Render to redeploy

## Testing:
- [ ] Tested Case Retrieval
- [ ] Tested Summarization
- [ ] Tested Chat (RAG)
- [ ] Tested Analytics
- [ ] All features working!

## Optional:
- [ ] Set up UptimeRobot to prevent spin-down
- [ ] Added custom domain
- [ ] Shared app URL with friends!

---

**Congratulations! Your app is live! 🎉**

Total time: ~25 minutes
Total cost: $0
