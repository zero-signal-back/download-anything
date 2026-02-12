#!/usr/bin/env python3
"""
Production startup script with health monitoring
"""
import os
import sys
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")
    try:
        import flask
        import yt_dlp
        import requests
        print("✅ All core dependencies installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_ffmpeg():
    """Check if ffmpeg is available"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg is installed")
            return True
    except:
        pass
    
    # Check local ffmpeg.exe
    if os.path.exists('ffmpeg.exe'):
        print("✅ Local ffmpeg.exe found")
        return True
    
    print("⚠️  FFmpeg not found (optional, needed for some formats)")
    return False

def setup_directories():
    """Create necessary directories"""
    print("Setting up directories...")
    dirs = ['downloads', 'logs']
    for d in dirs:
        Path(d).mkdir(exist_ok=True)
    print("✅ Directories ready")

def cleanup_old_files():
    """Clean up old download files"""
    print("Cleaning up old files...")
    try:
        import config
        cleanup_age = config.CLEANUP_AGE_HOURS * 3600
        count = 0
        
        for f in os.listdir('downloads'):
            filepath = os.path.join('downloads', f)
            if os.path.isfile(filepath):
                file_age = time.time() - os.path.getmtime(filepath)
                if file_age > cleanup_age:
                    os.remove(filepath)
                    count += 1
        
        if count > 0:
            print(f"✅ Cleaned {count} old files")
        else:
            print("✅ No old files to clean")
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def check_proxies():
    """Check if proxies are configured"""
    if os.path.exists('proxies.txt'):
        with open('proxies.txt', 'r') as f:
            lines = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            if lines:
                print(f"✅ {len(lines)} proxies configured")
                return True
    
    print("⚠️  No proxies configured (will use direct connection)")
    print("   Run: python proxy_scraper.py")
    return False

def main():
    print("="*60)
    print("🚀 Download Anything - Production Startup")
    print("="*60)
    print()
    
    # Pre-flight checks
    if not check_dependencies():
        sys.exit(1)
    
    check_ffmpeg()
    setup_directories()
    cleanup_old_files()
    check_proxies()
    
    print()
    print("="*60)
    print("✅ All checks passed! Starting server...")
    print("="*60)
    print()
    
    # Import and run app
    try:
        from app import app
        import config
        
        print(f"Server: http://{config.HOST}:{config.PORT}")
        print(f"Health: http://{config.HOST}:{config.PORT}/health")
        print()
        print("Press Ctrl+C to stop")
        print()
        
        app.run(
            debug=config.DEBUG,
            host=config.HOST,
            port=config.PORT,
            threaded=config.THREADED
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
