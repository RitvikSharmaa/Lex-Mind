# Deploy LexMind Frontend to Vercel

## Quick Deploy (Recommended)

### Step 1: Push to GitHub
Your code is already on GitHub at: https://github.com/RitvikSharmaa/Lex-Mind

### Step 2: Deploy to Vercel

1. Go to [Vercel](https://vercel.com)
2. Click "Add New" → "Project"
3. Import your GitHub repository: `RitvikSharmaa/Lex-Mind`
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

5. Add Environment Variable:
   - Key: `VITE_API_URL`
   - Value: `https://lex-mind-backend.onrender.com`

6. Click "Deploy"

### Step 3: Done!
Your app will be live at: `https://your-project-name.vercel.app`

## Alternative: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy from the root directory
vercel

# Follow the prompts:
# - Set up and deploy? Yes
# - Which scope? Your account
# - Link to existing project? No
# - Project name? lex-mind
# - In which directory is your code located? ./frontend
# - Override settings? Yes
#   - Build Command: npm run build
#   - Output Directory: dist
#   - Development Command: npm run dev

# Set environment variable
vercel env add VITE_API_URL production
# Enter: https://lex-mind-backend.onrender.com

# Deploy to production
vercel --prod
```

## Configuration Files

All configuration is already set up:
- ✅ `vercel.json` - Vercel configuration
- ✅ `frontend/.env.production` - Production environment variables
- ✅ `frontend/src/config.ts` - API URL configuration

## Backend URL

Your backend is already deployed at:
**https://lex-mind-backend.onrender.com**

The frontend is configured to use this URL automatically.

## Testing After Deployment

1. Visit your Vercel URL
2. Try the RAG Chat feature
3. Test case retrieval
4. Test summarization

## Troubleshooting

### CORS Issues
If you get CORS errors, update the backend's `FRONTEND_URL` environment variable on Render:
1. Go to Render dashboard
2. Select your backend service
3. Go to "Environment"
4. Add: `FRONTEND_URL=https://your-vercel-url.vercel.app`
5. Save and redeploy

### API Not Responding
- Check backend status: https://lex-mind-backend.onrender.com/health
- Wait for models to load (first request may take 30-60 seconds)
- Check Render logs for any errors

## Free Tier Limits

Vercel Free Tier:
- ✅ Unlimited deployments
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Custom domains
- ✅ Perfect for this project!

## Next Steps

After deployment:
1. Share your live URL!
2. Add custom domain (optional)
3. Monitor usage in Vercel dashboard
