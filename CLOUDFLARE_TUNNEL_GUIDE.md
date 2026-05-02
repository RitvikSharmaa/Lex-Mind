# Cloudflare Tunnel Setup Guide

Share your LexMind app with friends using Cloudflare Tunnel (completely FREE, no credit card needed!)

## What is Cloudflare Tunnel?

Cloudflare Tunnel creates a secure connection from your local machine to the internet through Cloudflare's network. Your friend can access your app via a public URL without you needing to configure firewalls or port forwarding.

## Prerequisites

- Your backend running on `http://localhost:5000`
- Your frontend running on `http://localhost:3000`
- Cloudflare account (free)

---

## Step 1: Install Cloudflare Tunnel (cloudflared)

### Windows Installation

**Option A: Using winget (Recommended)**
```bash
winget install --id Cloudflare.cloudflared
```

**Option B: Manual Download**
1. Download from: https://github.com/cloudflare/cloudflared/releases/latest
2. Download `cloudflared-windows-amd64.exe`
3. Rename it to `cloudflared.exe`
4. Move it to a folder in your PATH (or use full path when running)

### Verify Installation
```bash
cloudflared --version
```

---

## Step 2: Login to Cloudflare

```bash
cloudflared tunnel login
```

This will:
1. Open your browser
2. Ask you to select a domain (or use the default)
3. Authorize cloudflared
4. Save credentials to your computer

---

## Step 3: Create a Tunnel

```bash
cloudflared tunnel create lexmind-tunnel
```

This creates a tunnel and saves the credentials. Note the **Tunnel ID** shown in the output.

---

## Step 4: Create Tunnel Configuration

Create a file named `cloudflared-config.yml` in your project root:

```yaml
tunnel: lexmind-tunnel
credentials-file: C:\Users\YOUR_USERNAME\.cloudflared\TUNNEL_ID.json

ingress:
  # Route for frontend
  - hostname: lexmind.YOUR_DOMAIN.com
    service: http://localhost:3000
  
  # Route for backend API
  - hostname: lexmind-api.YOUR_DOMAIN.com
    service: http://localhost:5000
  
  # Catch-all rule (required)
  - service: http_status:404
```

**Important:** Replace:
- `YOUR_USERNAME` with your Windows username
- `TUNNEL_ID` with the tunnel ID from Step 3
- `YOUR_DOMAIN.com` with your Cloudflare domain

---

## Step 5: Configure DNS

```bash
cloudflared tunnel route dns lexmind-tunnel lexmind.YOUR_DOMAIN.com
cloudflared tunnel route dns lexmind-tunnel lexmind-api.YOUR_DOMAIN.com
```

This creates DNS records pointing to your tunnel.

---

## Step 6: Update Frontend API URL

Update `frontend/src/config.ts`:

```typescript
const config = {
  apiUrl: import.meta.env.PROD 
    ? 'https://lexmind-api.YOUR_DOMAIN.com'  // Your Cloudflare tunnel URL
    : 'http://localhost:5000'
};

export default config;
```

Rebuild frontend:
```bash
cd frontend
npm run build
npm run dev
```

---

## Step 7: Run the Tunnel

```bash
cloudflared tunnel --config cloudflared-config.yml run lexmind-tunnel
```

Your app is now live! Share these URLs with your friend:
- Frontend: `https://lexmind.YOUR_DOMAIN.com`
- Backend API: `https://lexmind-api.YOUR_DOMAIN.com`

---

## Quick Start (No Domain Required)

If you don't have a Cloudflare domain, use the **quick tunnel** method:

### For Frontend:
```bash
cloudflared tunnel --url http://localhost:3000
```

### For Backend (in another terminal):
```bash
cloudflared tunnel --url http://localhost:5000
```

This gives you temporary URLs like:
- `https://random-words-123.trycloudflare.com` (frontend)
- `https://random-words-456.trycloudflare.com` (backend)

**Update frontend config with the backend URL:**

1. Copy the backend tunnel URL
2. Update `frontend/src/config.ts`:
```typescript
const config = {
  apiUrl: 'https://random-words-456.trycloudflare.com'  // Your backend tunnel URL
};
```
3. Restart frontend: `npm run dev`

**Share the frontend URL with your friend!**

---

## Important Notes

1. **Keep terminals open**: The tunnel only works while `cloudflared` is running
2. **Backend must be running**: Make sure `python backend_api.py` is running
3. **Frontend must be running**: Make sure `npm run dev` is running in frontend folder
4. **CORS is configured**: Your backend already allows all origins
5. **Free forever**: Cloudflare Tunnel is completely free
6. **Temporary URLs**: Quick tunnel URLs change each time you restart
7. **Persistent URLs**: Use named tunnels with your domain for permanent URLs

---

## Troubleshooting

### "tunnel not found"
- Make sure you created the tunnel: `cloudflared tunnel create lexmind-tunnel`

### "connection refused"
- Check if backend is running: `http://localhost:5000/api/health`
- Check if frontend is running: `http://localhost:3000`

### "DNS record not found"
- Wait 1-2 minutes for DNS propagation
- Verify DNS: `cloudflared tunnel route dns lexmind-tunnel YOUR_HOSTNAME`

### Frontend can't reach backend
- Update `frontend/src/config.ts` with correct backend tunnel URL
- Rebuild frontend: `npm run dev`

---

## Stop the Tunnel

Press `Ctrl+C` in the terminal running cloudflared

---

## Alternative: Use ngrok (Simpler)

If Cloudflare Tunnel is too complex, try ngrok:

1. Install: https://ngrok.com/download
2. Run for backend: `ngrok http 5000`
3. Run for frontend: `ngrok http 3000`
4. Update frontend config with backend ngrok URL
5. Share frontend ngrok URL with friend

Both are free and work great!
