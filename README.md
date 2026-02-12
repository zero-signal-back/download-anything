# Download Anything - Universal Downloader

Production-ready multi-source download manager supporting 16+ platforms with rotating proxy support.

## Features
- 🚀 16+ source support (YouTube, Instagram, Telegram, etc.)
- 🔄 Rotating proxy support with auto-updater
- 📱 Responsive UI
- ⚡ High-quality downloads with retry mechanism
- 🎯 Quality selection (best, 2160p, 1440p, 1080p, 720p, 480p, 360p)
- 📦 Multiple format support
- 🛡️ Rate limiting & security features
- 🧹 Auto-cleanup of old files
- 💪 Production-ready with error handling

## Supported Sources
1. YouTube
2. Instagram (Reels/Posts)
3. Facebook
4. Twitter/X
5. Pinterest
6. Vimeo
7. Reddit
8. Google Drive
9. Mega.nz
10. MediaFire
11. GoFile.io
12. TeraBox
13. Doodstream
14. StreamTape
15. Archive.org
16. SlideShare
17. M3U8 Streams
18. Direct MP4/Video Links
19. Direct HTTP/HTTPS links

## Installation

```bash
# Clone repository
git clone <your-repo>
cd download-anything

# Install dependencies
pip install -r requirements.txt

# (Optional) Setup proxies
python proxy_scraper.py

# Run the application
python app.py
```

## Production Deployment

```bash
# Using Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 app:app --timeout 300

# Or with environment variables
export PORT=8080
export DEBUG=False
python app.py
```

## Usage

1. Open browser: http://localhost:5000
2. Paste your link
3. Select quality
4. Click Download
5. File will auto-download when ready

## Proxy Management

### Auto-update proxies
```bash
python proxy_scraper.py
```

### Manual proxy setup
Edit `proxies.txt`:
```
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
socks5://proxy3.example.com:1080
```

### Enable auto-updater in production
Uncomment in `app.py`:
```python
start_auto_updater(interval_hours=6)
```

## Troubleshooting

### Downloads failing?
1. Update proxies: `python proxy_scraper.py`
2. Check if site is supported
3. Try different quality settings
4. Check logs for specific errors

### Rate limit errors?
- Wait 60 seconds between requests
- Adjust `MAX_REQUESTS_PER_MINUTE` in config.py

### File not found?
- Files auto-delete after 24 hours
- Check `CLEANUP_AGE_HOURS` in config.py

## Configuration

Edit `config.py` to customize:
```python
MAX_DOWNLOAD_SIZE = 16 * 1024 * 1024 * 1024  # 16GB
DOWNLOAD_TIMEOUT = 300  # 5 minutes
MAX_RETRIES = 3
CLEANUP_AGE_HOURS = 24  # Auto-delete old files
MAX_REQUESTS_PER_MINUTE = 10  # Rate limiting
```

## Requirements
- Python 3.8+
- Flask 3.0+
- yt-dlp (latest)
- ffmpeg (for video processing)
- See requirements.txt for full list

## Performance Tips

1. Use Gunicorn with multiple workers
2. Enable proxy auto-updater for better success rates
3. Adjust timeout settings based on your network
4. Use CDN/reverse proxy (nginx) for static files
5. Monitor with `/health` endpoint

## API Endpoints

### Ping
```bash
GET /ping

Response: {"status": "ok", "message": "pong"}
```

### Health Check
```bash
GET /health

Response: {
  "status": "healthy",
  "timestamp": 1234567890,
  "active_downloads": 2
}
```

### Download
```bash
POST /download
Content-Type: application/json

{
  "url": "https://youtube.com/watch?v=...",
  "quality": "1080"  # optional: best, 2160, 1440, 1080, 720, 480, 360
}

Response: {"download_id": "123456"}
```

### Check Status
```bash
GET /status/<download_id>

Response: {
  "status": "completed",  # or "processing", "error"
  "file": "video.mp4"     # if completed
}
```

### Health Check
```bash
GET /health

Response: {
  "status": "healthy",
  "timestamp": 1234567890,
  "active_downloads": 2
}
```

### Download File
```bash
GET /file/<filename>
```

## Security Features

- ✅ Rate limiting (10 requests/minute per IP)
- ✅ Input validation & sanitization
- ✅ Path traversal protection
- ✅ URL validation
- ✅ File size limits (16GB max)
- ✅ Automatic cleanup of old files (24h)
- ✅ Error message sanitization

## Legal Notice
This tool is for downloading publicly available and legally accessible content only.
Users are responsible for complying with copyright laws and terms of service.
