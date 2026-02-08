# FFmpeg Installation Guide (Windows)

## Quick Install (Recommended)

### Method 1: Using Chocolatey (Easiest)
```bash
# Install Chocolatey first (if not installed)
# Run in PowerShell as Administrator:
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Then install ffmpeg:
choco install ffmpeg
```

### Method 2: Manual Download
1. Download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
2. Extract to `C:\ffmpeg`
3. Add to PATH:
   - Open "Environment Variables"
   - Edit "Path" variable
   - Add: `C:\ffmpeg\bin`
4. Restart terminal/cmd

### Method 3: Winget (Windows 11)
```bash
winget install ffmpeg
```

## Verify Installation
```bash
ffmpeg -version
```

## After Installation
Restart your Flask app:
```bash
python app.py
```

Now Instagram, M3U8 streams, and video merging will work!
