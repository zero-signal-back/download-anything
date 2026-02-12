from flask import Flask, render_template, request, jsonify, send_file
from downloader import DownloadManager
from username_checker import UsernameChecker
from auto_proxy_updater import start_auto_updater
from video_tools import VideoTools
import config
import os
import threading
import time
import re
import logging
from functools import wraps
from collections import defaultdict
from logging.handlers import RotatingFileHandler
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = config.MAX_DOWNLOAD_SIZE
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Setup logging
if not config.DEBUG:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240000, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Download Anything startup')

download_manager = DownloadManager(app.config['DOWNLOAD_FOLDER'])
username_checker = UsernameChecker()
video_tools = VideoTools(app.config['DOWNLOAD_FOLDER'])
download_status = {}

# Rate limiting
request_counts = defaultdict(list)

def rate_limit(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        ip = request.remote_addr
        now = time.time()
        
        request_counts[ip] = [t for t in request_counts[ip] if now - t < config.RATE_LIMIT_WINDOW]
        
        if len(request_counts[ip]) >= config.MAX_REQUESTS_PER_MINUTE:
            return jsonify({'error': 'Rate limit exceeded. Try again later.'}), 429
        
        request_counts[ip].append(now)
        return f(*args, **kwargs)
    return decorated_function

def validate_url(url):
    """Validate URL format"""
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        return False
    if len(url) > config.MAX_URL_LENGTH:
        return False
    return True

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'active_downloads': len([s for s in download_status.values() if s.get('status') == 'processing'])
    })

@app.route('/ping')
def ping():
    """Simple ping endpoint"""
    return jsonify({'status': 'ok', 'message': 'pong'})

@app.route('/username-finder')
def username_finder():
    return render_template('username.html')

@app.route('/do-anything')
def do_anything():
    return render_template('do_anything.html')

@app.route('/tool/watermark-remover')
def tool_watermark():
    return render_template('tool_watermark.html')

@app.route('/tool/video-to-gif')
def tool_gif():
    return render_template('tool_gif.html')

@app.route('/tool/video-compressor')
def tool_compress():
    return render_template('tool_compress.html')

@app.route('/tool/format-converter')
def tool_convert():
    return render_template('tool_convert.html')

@app.route('/tool/video-rotator')
def tool_rotate():
    return render_template('tool_rotate.html')

@app.route('/download', methods=['POST'])
@rate_limit
def download():
    data = request.json
    url = data.get('url', '').strip()
    quality = data.get('quality', 'best')
    audio_only = data.get('audio_only', False)
    
    if not validate_url(url):
        return jsonify({'error': 'Invalid URL format'}), 400
    
    # Validate quality
    valid_qualities = ['best', '2160', '1440', '1080', '720', '480', '360']
    if quality not in valid_qualities:
        quality = 'best'
    
    download_id = str(hash(url + str(time.time())))
    download_status[download_id] = {'status': 'processing', 'progress': 0}
    
    def download_task():
        try:
            app.logger.info(f"Starting download: {url[:100]} (audio_only={audio_only})")
            result = download_manager.download(url, quality, audio_only=audio_only)
            if result:
                download_status[download_id] = {'status': 'completed', 'file': result, 'timestamp': time.time()}
                app.logger.info(f"Download completed: {result}")
            else:
                download_status[download_id] = {'status': 'error', 'message': 'Download failed - no file returned', 'timestamp': time.time()}
                app.logger.error(f"Download failed: no file returned for {url[:100]}")
        except Exception as e:
            error_msg = str(e)[:500]
            download_status[download_id] = {'status': 'error', 'message': error_msg, 'timestamp': time.time()}
            app.logger.error(f"Download error: {error_msg} for {url[:100]}")
    
    thread = threading.Thread(target=download_task, daemon=True)
    thread.start()
    
    return jsonify({'download_id': download_id})

@app.route('/status/<download_id>')
def status(download_id):
    status_data = download_status.get(download_id, {'status': 'not_found'})
    
    # Clean up completed/error downloads after 1 hour
    if status_data.get('status') in ['completed', 'error']:
        if 'timestamp' not in status_data:
            status_data['timestamp'] = time.time()
        elif time.time() - status_data['timestamp'] > 3600:
            download_status.pop(download_id, None)
    
    return jsonify(status_data)

@app.route('/search-username', methods=['POST'])
@rate_limit
def search_username():
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    # Validate username - allow alphanumeric, underscore, dot, hyphen
    if not re.match(r'^[a-zA-Z0-9_.\-]{2,30}$', username):
        return jsonify({'error': 'Invalid username format (2-30 chars, alphanumeric only)'}), 400
    
    results = username_checker.search_username(username)
    return jsonify(results)

@app.route('/file/<path:filename>')
def download_file(filename):
    # Prevent path traversal
    filename = os.path.basename(filename)
    filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    # Verify file is in download folder
    if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['DOWNLOAD_FOLDER'])):
        return jsonify({'error': 'Access denied'}), 403
    
    import mimetypes
    mimetype = mimetypes.guess_type(filepath)[0]
    
    if mimetype and mimetype.startswith('video'):
        return send_file(filepath, mimetype=mimetype)
    else:
        return send_file(filepath, as_attachment=True)

@app.route('/download-file/<path:filename>')
def download_file_attachment(filename):
    filename = os.path.basename(filename)
    filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    if not os.path.abspath(filepath).startswith(os.path.abspath(app.config['DOWNLOAD_FOLDER'])):
        return jsonify({'error': 'Access denied'}), 403
    
    return send_file(filepath, as_attachment=True)

@app.route('/remove-watermark', methods=['POST'])
@rate_limit
def remove_watermark():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    watermark_type = request.form.get('type', 'tiktok')
    
    try:
        filename = secure_filename(video.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(upload_path)
        
        if watermark_type == 'tiktok':
            result = video_tools.remove_tiktok_watermark(upload_path)
        elif watermark_type == 'instagram':
            result = video_tools.remove_instagram_watermark(upload_path)
        else:
            x = int(request.form.get('x', 0))
            y = int(request.form.get('y', 0))
            width = int(request.form.get('width', 200))
            height = int(request.form.get('height', 100))
            result = video_tools.remove_watermark(upload_path, x, y, width, height)
        
        os.remove(upload_path)
        return jsonify({'success': True, 'filename': result})
    except Exception as e:
        app.logger.error(f"Watermark removal error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/video-to-gif', methods=['POST'])
@rate_limit
def video_to_gif():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        filename = secure_filename(video.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(upload_path)
        
        start = float(request.form.get('start', 0))
        duration = float(request.form.get('duration', 5))
        fps = int(request.form.get('fps', 15))
        
        result = video_tools.video_to_gif(upload_path, start, duration, fps)
        
        os.remove(upload_path)
        return jsonify({'success': True, 'filename': result})
    except Exception as e:
        app.logger.error(f"GIF conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/compress-video', methods=['POST'])
@rate_limit
def compress_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        filename = secure_filename(video.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(upload_path)
        
        original_size = os.path.getsize(upload_path)
        quality = request.form.get('quality', 'medium')
        
        result = video_tools.compress_video(upload_path, quality)
        
        compressed_size = os.path.getsize(os.path.join(app.config['DOWNLOAD_FOLDER'], result))
        
        os.remove(upload_path)
        
        def format_size(size):
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} TB"
        
        return jsonify({
            'success': True,
            'filename': result,
            'original_size': format_size(original_size),
            'compressed_size': format_size(compressed_size)
        })
    except Exception as e:
        app.logger.error(f"Compression error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/convert-format', methods=['POST'])
@rate_limit
def convert_format():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        filename = secure_filename(video.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(upload_path)
        
        output_format = request.form.get('format', 'mp4')
        result = video_tools.convert_format(upload_path, output_format)
        
        os.remove(upload_path)
        return jsonify({'success': True, 'filename': result})
    except Exception as e:
        app.logger.error(f"Format conversion error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/rotate-video', methods=['POST'])
@rate_limit
def rotate_video():
    if 'video' not in request.files:
        return jsonify({'success': False, 'error': 'No video file'}), 400
    
    video = request.files['video']
    if video.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    try:
        filename = secure_filename(video.filename)
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        video.save(upload_path)
        
        rotation = request.form.get('rotation', '90')
        result = video_tools.rotate_video(upload_path, rotation)
        
        os.remove(upload_path)
        return jsonify({'success': True, 'filename': result})
    except Exception as e:
        app.logger.error(f"Rotation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    app.logger.warning(f"File too large from {request.remote_addr}")
    return jsonify({'error': 'File too large'}), 413

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    # Handle favicon requests silently
    if 'favicon.ico' in str(error):
        return '', 204
    return jsonify({'error': 'Not found'}), 404

if __name__ == '__main__':
    # Clean old downloads on startup
    try:
        cleanup_age = config.CLEANUP_AGE_HOURS * 3600
        for f in os.listdir(app.config['DOWNLOAD_FOLDER']):
            filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], f)
            if os.path.isfile(filepath):
                file_age = time.time() - os.path.getmtime(filepath)
                if file_age > cleanup_age:
                    os.remove(filepath)
                    print(f"Cleaned old file: {f}")
    except Exception as e:
        print(f"Cleanup error: {e}")
    
    print(f"Starting server on {config.HOST}:{config.PORT}")
    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT, threaded=config.THREADED)
