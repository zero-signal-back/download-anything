# Download Anything - Universal Downloader

Multi-source download manager supporting 16+ platforms with rotating proxy support.

## Features
- 🚀 16+ source support
- 🔄 Rotating proxy support
- 📱 Responsive UI
- ⚡ High-quality downloads
- 🎯 Quality selection
- 📦 Multiple format support

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
# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

## Usage

1. Open browser: http://localhost:5000
2. Paste your link
3. Select quality
4. Click Download
5. File will auto-download when ready

## Proxy Setup

Edit `proxies.txt` and add your proxies:
```
http://proxy1.example.com:8080
http://user:pass@proxy2.example.com:8080
socks5://proxy3.example.com:1080
```

## Configuration

Edit `downloader.py` to customize:
- Add more proxies in `load_proxies()`
- Modify download paths
- Add custom handlers

## Requirements
- Python 3.8+
- Flask
- yt-dlp
- instaloader
- mega.py
- gdown
- requests

## Notes
- Downloads saved in `downloads/` folder
- Supports quality selection (best, 1080p, 720p, 480p, 360p)
- Automatic format detection
- Thread-based async downloads

## Legal Notice
This tool is for downloading publicly available and legally accessible content only.
Users are responsible for complying with copyright laws and terms of service.
