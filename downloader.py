import yt_dlp
import instaloader
import gdown
import requests
import re
try:
    from mega import Mega
    MEGA_AVAILABLE = True
except:
    MEGA_AVAILABLE = False
from internetarchive import download as ia_download
import os
import random
import subprocess
from urllib.parse import urlparse
import asyncio
import time
import hashlib
import config
try:
    from telethon import TelegramClient
    from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto
    import telegram_config
    TELETHON_AVAILABLE = True
except:
    TELETHON_AVAILABLE = False

class DownloadManager:
    def __init__(self, download_folder):
        self.download_folder = download_folder
        self.proxies = self.load_proxies()
        self.max_retries = config.MAX_RETRIES
        self.timeout = config.DOWNLOAD_TIMEOUT
        
    def load_proxies(self):
        proxies = []  # No default None
        try:
            if os.path.exists('proxies.txt'):
                with open('proxies.txt', 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            proxies.append(line)
        except Exception as e:
            print(f"Error loading proxies: {e}")
        
        # If no proxies loaded, return None for direct connection
        if not proxies:
            return [None]
        return proxies
    
    def get_random_proxy(self):
        return random.choice(self.proxies)
    
    def sanitize_filename(self, filename):
        """Remove invalid characters from filename"""
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        filename = filename[:200]  # Limit length
        return filename
    
    def retry_download(self, func, *args, **kwargs):
        """Retry download with exponential backoff"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise e
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1}/{self.max_retries} after {wait_time}s...")
                time.sleep(wait_time)
    
    def download(self, url, quality='best', audio_only=False):
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            raise Exception("Invalid URL format")
        
        domain = urlparse(url).netloc.lower()
        
        # If audio only requested, use audio downloader
        if audio_only:
            return self.download_audio(url)
        
        # YouTube
        if 'youtube.com' in domain or 'youtu.be' in domain:
            return self.download_youtube(url, quality)
        
        # Telegram
        elif 't.me' in domain or 'telegram.me' in domain or 'telegram.org' in domain:
            return self.download_telegram(url, quality)
        
        # Dailymotion
        elif 'dailymotion.com' in domain:
            return self.download_dailymotion(url, quality)
        
        # Instagram
        elif 'instagram.com' in domain:
            return self.download_instagram_api(url)
        
        # Mega
        elif 'mega.nz' in domain or 'mega.io' in domain:
            return self.download_mega(url)
        
        # Google Drive
        elif 'drive.google.com' in domain:
            return self.download_gdrive(url)
        
        # GoFile
        elif 'gofile.io' in domain:
            return self.download_gofile(url)
        
        # TeraBox
        elif 'terabox' in domain or 'terasharefile.com' in domain:
            return self.download_terabox(url)
        
        # Archive.org
        elif 'archive.org' in domain:
            return self.download_archive(url)
        
        # M3U8 streams
        elif '.m3u8' in url.lower():
            return self.download_m3u8(url)
        
        # Direct MP4/video links
        elif url.startswith('http') and any(ext in url.lower() for ext in ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.webm']):
            return self.download_direct(url)
        
        # Other direct links
        elif url.startswith('http') and any(ext in url.lower() for ext in ['.pdf', '.zip', '.rar', '.jpg', '.png']):
            return self.download_direct(url)
        
        # Adult content sites (videos + cam sites)
        elif any(site in domain for site in ['camgirlsleak.com', 'pornhub.com', 'xvideos.com', 'xnxx.com', 'redtube.com', 'youporn.com', 'spankbang.com', 'eporner.com', 'xhamster.com', 'chaturbate.com', 'stripchat.com', 'cam4.com', 'bongacams.com', 'myfreecams.com', 'camsoda.com', 'livejasmin.com']):
            return self.download_adult_site(url, quality)
        
        # Live streams (RTMP, RTSP, HLS, DASH)
        elif any(protocol in url.lower() for protocol in ['rtmp://', 'rtmps://', 'rtsp://', 'rtsps://']):
            return self.download_live_stream(url)
        
        # HLS/DASH manifests
        elif any(ext in url.lower() for ext in ['.mpd', '.m3u', '.m3u8']):
            return self.download_streaming_manifest(url)
        
        # Default: yt-dlp (supports 1000+ sites)
        else:
            return self.download_ytdlp(url, quality)
    
    def download_ytdlp(self, url, quality):
        proxy = self.get_random_proxy()
        
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best' if quality != 'best' else 'best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'quiet': False,
            'socket_timeout': self.timeout,
            'retries': self.max_retries,
            'fragment_retries': self.max_retries,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5'
            }
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return self.sanitize_filename(os.path.basename(filename))
    
    def download_audio(self, url):
        """Download audio only (MP3)"""
        proxy = self.get_random_proxy()
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'quiet': False,
            'socket_timeout': self.timeout,
            'retries': self.max_retries,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5'
            }
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # After conversion, filename will have .mp3 extension
            filename = ydl.prepare_filename(info)
            # Replace extension with .mp3
            filename_base = os.path.splitext(filename)[0]
            mp3_filename = filename_base + '.mp3'
            return self.sanitize_filename(os.path.basename(mp3_filename))
    
    def download_youtube(self, url, quality):
        proxy = self.get_random_proxy()
        
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best' if quality != 'best' else 'best',
            'outtmpl': os.path.join(self.download_folder, '%(title)s.%(ext)s'),
            'merge_output_format': 'mp4',
            'quiet': False,
            'no_warnings': False,
            'socket_timeout': self.timeout,
            'retries': self.max_retries,
            'fragment_retries': self.max_retries,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web'],
                    'skip': ['hls', 'dash']
                }
            },
            'http_headers': {
                'User-Agent': 'com.google.android.youtube/17.36.4 (Linux; U; Android 12; GB) gzip',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            }
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return self.sanitize_filename(os.path.basename(filename))
    
    def download_dailymotion(self, url, quality):
        proxy = self.get_random_proxy()
        timestamp = int(time.time())
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_folder, f'{timestamp}_%(title)s.%(ext)s'),
            'quiet': False,
            'no_check_certificate': True,
            'geo_bypass': True,
            'socket_timeout': self.timeout,
            'retries': self.max_retries,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': '*/*',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': 'https://www.dailymotion.com/'
            }
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return self.sanitize_filename(os.path.basename(filename))
    
    def download_telegram(self, url, quality):
        # Check if it's a private channel (/c/ in URL)
        if '/c/' in url:
            raise Exception("Private Telegram channels are not supported. Please use public Telegram links only.")
        
        # Public channels - use yt-dlp
        proxy = self.get_random_proxy()
        timestamp = int(time.time())
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_folder, f'{timestamp}_%(title)s.%(ext)s'),
            'quiet': False,
            'socket_timeout': self.timeout,
            'retries': self.max_retries,
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info is None:
                    raise Exception("Video not found or not accessible. Please check the link.")
                filename = ydl.prepare_filename(info)
                return self.sanitize_filename(os.path.basename(filename))
        except Exception as e:
            if 'Private Telegram' in str(e):
                raise e
            raise Exception(f"Video not found or not accessible. Please check the link.")
    
    async def download_telegram_private(self, url):
        """Disabled - Private channels not supported"""
        raise Exception("Private Telegram channels are not supported. Please use public Telegram links only.")
    
    def download_instagram_api(self, url):
        """Download Instagram using RapidAPI Downloader"""
        try:
            # Extract shortcode from URL
            if '/p/' in url or '/reel/' in url or '/tv/' in url:
                shortcode = url.split('/')[-2].split('?')[0]
            else:
                raise Exception("Invalid Instagram URL format")
            
            timestamp = int(time.time())
            
            # Method 1: Try Instaloader (works for public posts)
            try:
                L = instaloader.Instaloader(
                    dirname_pattern=self.download_folder,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False,
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                )
                
                post = instaloader.Post.from_shortcode(L.context, shortcode)
                L.download_post(post, target='')
                
                # Get the downloaded file
                files = [f for f in os.listdir(self.download_folder) 
                        if f.endswith(('.mp4', '.jpg', '.jpeg', '.png')) and 
                        not f.endswith('.json.xz') and
                        os.path.getmtime(os.path.join(self.download_folder, f)) > time.time() - 60]
                
                if files:
                    latest = max([os.path.join(self.download_folder, f) for f in files], key=os.path.getctime)
                    new_name = f"{timestamp}_instagram{os.path.splitext(latest)[1]}"
                    new_path = os.path.join(self.download_folder, new_name)
                    os.rename(latest, new_path)
                    
                    # Clean up extra files
                    for f in os.listdir(self.download_folder):
                        if f.endswith(('.json.xz', '.txt')) and shortcode in f:
                            try:
                                os.remove(os.path.join(self.download_folder, f))
                            except:
                                pass
                    
                    return new_name
            except Exception as e:
                print(f"Instaloader failed: {e}")
            
            # Method 2: Try yt-dlp with cookies
            try:
                proxy = self.get_random_proxy()
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(self.download_folder, f'{timestamp}_instagram.%(ext)s'),
                    'quiet': False,
                    'cookiesfrombrowser': ('chrome',),
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
                        'Referer': 'https://www.instagram.com/'
                    }
                }
                
                if proxy:
                    ydl_opts['proxy'] = proxy
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    if info:
                        filename = ydl.prepare_filename(info)
                        return os.path.basename(filename)
            except Exception as e:
                print(f"yt-dlp method failed: {e}")
            
            raise Exception("Instagram download failed. The post may be private or deleted. Try a public post.")
            
        except Exception as e:
            raise Exception(f"Instagram download failed: {str(e)}")

        """Download Instagram using yt-dlp (more reliable than instaloader)"""
        try:
            timestamp = int(time.time())
            
            proxy = self.get_random_proxy()
            
            ydl_opts = {
                'format': 'best',
                'outtmpl': os.path.join(self.download_folder, f'{timestamp}_%(title)s.%(ext)s'),
                'quiet': False,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': 'https://www.instagram.com/'
                }
            }
            
            if proxy:
                ydl_opts['proxy'] = proxy
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return os.path.basename(filename)
                
        except Exception as e:
            print(f"Instagram yt-dlp error: {e}")
            # Fallback to instaloader
            try:
                L = instaloader.Instaloader(
                    dirname_pattern=self.download_folder,
                    download_video_thumbnails=False,
                    download_geotags=False,
                    download_comments=False,
                    save_metadata=False,
                    compress_json=False,
                    user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15'
                )
                
                if '/p/' in url or '/reel/' in url:
                    shortcode = url.split('/')[-2]
                    post = instaloader.Post.from_shortcode(L.context, shortcode)
                    L.download_post(post, target='')
                    
                    # Get only video/image files (not json/txt)
                    files = [f for f in os.listdir(self.download_folder) 
                            if f.endswith(('.mp4', '.jpg', '.jpeg', '.png')) and not f.endswith('.json.xz')]
                    
                    if files:
                        latest = max([os.path.join(self.download_folder, f) for f in files], key=os.path.getctime)
                        return os.path.basename(latest)
                
                raise Exception("Instagram download failed. Could not find media file.")
            except Exception as e2:
                print(f"Instagram instaloader error: {e2}")
                raise Exception(f"Instagram download failed. The post may be private or require login. Try a public post.")
    
    def download_mega(self, url):
        if not MEGA_AVAILABLE:
            # Fallback to yt-dlp for mega
            return self.download_ytdlp(url, 'best')
        
        try:
            m = Mega()
            file = m.download_url(url, self.download_folder)
            return os.path.basename(file)
        except:
            # Fallback to yt-dlp
            return self.download_ytdlp(url, 'best')
    
    def download_gdrive(self, url):
        output = os.path.join(self.download_folder, 'gdrive_file')
        gdown.download(url, output, quiet=False, fuzzy=True)
        
        files = os.listdir(self.download_folder)
        latest = max([os.path.join(self.download_folder, f) for f in files], key=os.path.getctime)
        return os.path.basename(latest)
    
    def download_gofile(self, url):
        proxy = self.get_random_proxy()
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        response = requests.get(url, proxies=proxies)
        
        # GoFile requires token and content ID parsing
        # Simplified version - you may need to enhance this
        content_id = url.split('/')[-1]
        
        # Get download link
        api_url = f'https://api.gofile.io/getContent?contentId={content_id}'
        data = requests.get(api_url, proxies=proxies).json()
        
        if data['status'] == 'ok':
            files = data['data']['contents']
            for file_id, file_info in files.items():
                download_url = file_info['link']
                filename = file_info['name']
                
                file_response = requests.get(download_url, proxies=proxies, stream=True)
                filepath = os.path.join(self.download_folder, filename)
                
                with open(filepath, 'wb') as f:
                    for chunk in file_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                return filename
        
        return None
    
    def download_terabox(self, url):
        # TeraBox requires browser automation
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.service import Service
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from webdriver_manager.chrome import ChromeDriverManager
            import time
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Preferences for auto download
            prefs = {
                'download.default_directory': os.path.abspath(self.download_folder),
                'download.prompt_for_download': False,
                'download.directory_upgrade': True,
                'safebrowsing.enabled': True
            }
            chrome_options.add_experimental_option('prefs', prefs)
            
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            
            try:
                print(f"Opening TeraBox link: {url}")
                driver.get(url)
                time.sleep(8)  # Wait for page load
                
                # Multiple selectors to try
                selectors = [
                    "//button[contains(@class, 'download')]",
                    "//a[contains(@class, 'download')]",
                    "//button[contains(text(), 'Download')]",
                    "//a[contains(text(), 'Download')]",
                    "//button[contains(text(), 'download')]",
                    "//a[contains(text(), 'download')]",
                    "//div[contains(@class, 'download-btn')]",
                    "//span[contains(text(), 'Download')]/parent::button",
                    "//i[contains(@class, 'download')]/parent::button",
                    "//button[@type='button' and contains(., 'Download')]",
                ]
                
                download_clicked = False
                for selector in selectors:
                    try:
                        print(f"Trying selector: {selector}")
                        element = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        element.click()
                        print("Download button clicked!")
                        download_clicked = True
                        break
                    except:
                        continue
                
                if download_clicked:
                    time.sleep(15)  # Wait for download
                    
                    # Get latest file
                    files = [f for f in os.listdir(self.download_folder) if not f.endswith('.crdownload')]
                    if files:
                        latest = max([os.path.join(self.download_folder, f) for f in files], key=os.path.getctime)
                        driver.quit()
                        return os.path.basename(latest)
                
                # If no download button found, try to get direct link from page
                try:
                    page_source = driver.page_source
                    driver.quit()
                    
                    # Look for direct download links in page source
                    import re
                    video_patterns = [
                        r'"(https?://[^"]*\.mp4[^"]*)"',
                        r'"(https?://[^"]*\.mkv[^"]*)"',
                        r'"url":"([^"]+)"',
                    ]
                    
                    for pattern in video_patterns:
                        matches = re.findall(pattern, page_source)
                        if matches:
                            direct_url = matches[0]
                            print(f"Found direct URL: {direct_url}")
                            return self.download_direct(direct_url)
                except:
                    pass
                
                driver.quit()
                raise Exception("TeraBox: Could not find download button or direct link. Link may require login, be password protected, or expired.")
                
            except Exception as e:
                driver.quit()
                raise e
                
        except ImportError:
            raise Exception("Selenium not installed. Run: pip install selenium webdriver-manager")
        except Exception as e:
            raise Exception(f"TeraBox download failed: {str(e)}")
    
    def download_archive(self, url):
        identifier = url.split('/')[-1]
        ia_download(identifier, destdir=self.download_folder)
        
        files = os.listdir(self.download_folder)
        latest = max([os.path.join(self.download_folder, f) for f in files], key=os.path.getctime)
        return os.path.basename(latest)
    
    def download_m3u8(self, url):
        proxy = self.get_random_proxy()
        
        filename = f"video_{hash(url)}.mp4"
        filepath = os.path.join(self.download_folder, filename)
        
        # Use ffmpeg for m3u8 streams
        if proxy:
            cmd = ['ffmpeg', '-http_proxy', proxy, '-i', url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', filepath]
        else:
            cmd = ['ffmpeg', '-i', url, '-c', 'copy', '-bsf:a', 'aac_adtstoasc', filepath]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return filename
        except:
            # Fallback to yt-dlp for m3u8
            ydl_opts = {
                'format': 'best',
                'outtmpl': filepath,
            }
            if proxy:
                ydl_opts['proxy'] = proxy
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return filename
    
    def download_adult_site(self, url, quality):
        """Download from adult content sites (videos + cam recordings)"""
        proxy = self.get_random_proxy()
        timestamp = int(time.time())
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': os.path.join(self.download_folder, f'{timestamp}_video.%(ext)s'),
            'quiet': False,
            'no_check_certificate': True,
            'age_limit': 21,
            'extractor_args': {'generic': {'allowed_extractors': ['generic', 'html5']}},
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Referer': url,
            }
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                return os.path.basename(filename)
        except Exception as e:
            # Try to extract direct video/stream URL from page
            try:
                response = requests.get(url, headers=ydl_opts['http_headers'])
                html = response.text
                
                # Look for video URLs and streaming URLs
                import re
                patterns = [
                    r'"(https?://[^"]*\.mp4[^"]*)"',
                    r"'(https?://[^']*\.mp4[^']*)'",
                    r'src="(https?://[^"]*\.mp4[^"]*)"',
                    r'file:"([^"]+\.mp4)"',
                    r'video_url":"([^"]+)"',
                    r'videoUrl":"([^"]+)"',
                    r'"(https?://[^"]*\.m3u8[^"]*)"',  # HLS streams
                    r'hlsUrl":"([^"]+)"',
                    r'stream_url":"([^"]+)"',
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, html)
                    if matches:
                        video_url = matches[0].replace('\\/', '/')
                        print(f"Found video/stream URL: {video_url}")
                        if '.m3u8' in video_url:
                            return self.download_m3u8(video_url)
                        else:
                            return self.download_direct(video_url)
                
                raise Exception(f"Could not extract video from this site. Error: {str(e)}")
            except:
                raise Exception(f"Failed to download from this site. The video may be protected or require login.")
    
    def download_live_stream(self, url):
        """Download RTMP/RTSP live streams"""
        timestamp = int(time.time())
        filename = f"{timestamp}_livestream.mp4"
        filepath = os.path.join(self.download_folder, filename)
        
        try:
            # Use FFmpeg to capture live stream
            cmd = [
                'ffmpeg',
                '-i', url,
                '-c', 'copy',
                '-t', '3600',  # Max 1 hour recording
                '-bsf:a', 'aac_adtstoasc',
                filepath
            ]
            
            subprocess.run(cmd, check=True, capture_output=True, timeout=3600)
            return filename
        except subprocess.TimeoutExpired:
            # If timeout, return partial recording
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return filename
            raise Exception("Live stream recording timeout")
        except Exception as e:
            raise Exception(f"Live stream download failed: {str(e)}")
    
    def download_streaming_manifest(self, url):
        """Download HLS (.m3u8) or DASH (.mpd) streams"""
        if '.m3u8' in url.lower():
            return self.download_m3u8(url)
        
        # DASH manifest
        proxy = self.get_random_proxy()
        timestamp = int(time.time())
        filename = f"{timestamp}_stream.mp4"
        filepath = os.path.join(self.download_folder, filename)
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': filepath,
            'quiet': False,
        }
        
        if proxy:
            ydl_opts['proxy'] = proxy
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return filename
        except Exception as e:
            raise Exception(f"Streaming manifest download failed: {str(e)}")
    
    def download_direct(self, url):
        proxy = self.get_random_proxy()
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        
        filename = url.split('/')[-1].split('?')[0]
        if not filename or '.' not in filename:
            filename = f"download_{hashlib.md5(url.encode()).hexdigest()[:8]}.mp4"
        
        filename = self.sanitize_filename(filename)
        filepath = os.path.join(self.download_folder, filename)
        
        response = requests.get(url, proxies=proxies, stream=True, timeout=self.timeout, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return filename
    
    def download_subtitles(self, url, format_type='srt'):
        """Download subtitles from YouTube"""
        try:
            ydl_opts = {
                'skip_download': True,
                'writesubtitles': True,
                'writeautomaticsub': True,
                'subtitlesformat': format_type,
                'quiet': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    return None
                
                subtitles = []
                
                # Get available subtitles
                if 'subtitles' in info and info['subtitles']:
                    for lang, subs in info['subtitles'].items():
                        for sub in subs:
                            if sub.get('url'):
                                subtitles.append({
                                    'language': lang,
                                    'url': sub['url'],
                                    'ext': sub.get('ext', format_type)
                                })
                
                # Get automatic captions if no manual subtitles
                if not subtitles and 'automatic_captions' in info and info['automatic_captions']:
                    for lang, subs in info['automatic_captions'].items():
                        for sub in subs:
                            if sub.get('url'):
                                subtitles.append({
                                    'language': f"{lang} (auto)",
                                    'url': sub['url'],
                                    'ext': sub.get('ext', format_type)
                                })
                
                return subtitles if subtitles else None
                
        except Exception as e:
            raise Exception(f"Subtitle download failed: {str(e)}")
