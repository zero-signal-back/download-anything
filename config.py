# Production Configuration
import os

# Download settings
MAX_DOWNLOAD_SIZE = 16 * 1024 * 1024 * 1024  # 16GB
DOWNLOAD_TIMEOUT = 300  # 5 minutes
MAX_RETRIES = 3
CLEANUP_AGE_HOURS = 24  # Delete files older than 24 hours

# Rate limiting
MAX_REQUESTS_PER_MINUTE = 10
RATE_LIMIT_WINDOW = 60  # seconds

# Proxy settings
PROXY_UPDATE_INTERVAL = 6  # hours
MAX_PROXY_TEST = 100
PROXY_TIMEOUT = 3  # seconds

# Server settings
HOST = '0.0.0.0'
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
THREADED = True

# Security
MAX_URL_LENGTH = 2048
ALLOWED_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm', 
                      '.pdf', '.zip', '.rar', '.jpg', '.png', '.jpeg', '.gif'}
