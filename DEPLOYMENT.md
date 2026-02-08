# 🚀 Render Deployment Guide

## Step 1: GitHub Setup

### Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `download-anything`
3. Make it **Public** or **Private**
4. Click "Create repository"

### Upload Code to GitHub
```bash
# Open terminal in project folder
cd C:\Users\shado\python\download-anything

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Download Anything"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/download-anything.git

# Push to GitHub
git branch -M main
git push -u origin main
```

---

## Step 2: Render Deployment

### Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repositories

### Deploy Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `download-anything`
3. Configure:
   - **Name**: `download-anything`
   - **Region**: Singapore (closest to India)
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `bash build.sh`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`

4. Click **"Create Web Service"**

### Wait for Deployment
- Build takes 5-10 minutes
- FFmpeg will auto-install
- You'll get a URL: `https://download-anything.onrender.com`

---

## Step 3: Test Your Live Site

### Your Live URL
```
https://download-anything.onrender.com
```

### Test Links
1. YouTube: `https://youtube.com/watch?v=dQw4w9WgXcQ`
2. Instagram: Any public reel
3. Twitter: Any video tweet
4. Direct MP4: Any .mp4 link

---

## 🎯 Important Notes

### Free Tier Limitations
- ✅ FFmpeg included
- ✅ Unlimited bandwidth
- ⚠️ Sleeps after 15 min inactivity (wakes up in 30 sec)
- ⚠️ 750 hours/month free

### Keep Site Awake (Optional)
Use **UptimeRobot** (free):
1. Go to https://uptimerobot.com
2. Add monitor: Your Render URL
3. Check every 5 minutes
4. Site stays awake 24/7

---

## 🔧 Troubleshooting

### Build Failed?
- Check `build.sh` has correct permissions
- Verify `requirements.txt` is correct
- Check Render logs for errors

### FFmpeg Not Working?
- Render auto-installs FFmpeg via `build.sh`
- Check logs: "ffmpeg installed successfully"

### Site Slow?
- Free tier has limited resources
- Upgrade to paid ($7/month) for better performance

---

## 💡 Next Steps

### Custom Domain (Optional)
1. Buy domain from Namecheap/GoDaddy
2. Add to Render settings
3. Update DNS records

### Monetization
1. Add Google AdSense
2. Premium features (₹99/month)
3. API access for developers

### Marketing
1. Share on Reddit (r/InternetIsBeautiful)
2. Twitter/Instagram posts
3. Product Hunt launch

---

## 📊 Monitor Traffic

### Render Dashboard
- View logs
- Check usage
- Monitor errors

### Google Analytics (Optional)
Add tracking code to `templates/index.html`

---

## 🎉 You're Live!

Your site is now accessible worldwide at:
**https://download-anything.onrender.com**

Share the link and get users! 🚀
