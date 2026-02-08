from flask import Flask, render_template, request, jsonify, send_file
from downloader import DownloadManager
from username_checker import UsernameChecker
from auto_proxy_updater import start_auto_updater
import os
import threading

app = Flask(__name__)
app.config['DOWNLOAD_FOLDER'] = 'downloads'
os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

download_manager = DownloadManager(app.config['DOWNLOAD_FOLDER'])
username_checker = UsernameChecker()
download_status = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/username-finder')
def username_finder():
    return render_template('username.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    quality = data.get('quality', 'best')
    
    if not url:
        return jsonify({'error': 'URL required'}), 400
    
    download_id = str(hash(url + str(threading.get_ident())))
    download_status[download_id] = {'status': 'processing', 'progress': 0}
    
    def download_task():
        try:
            result = download_manager.download(url, quality)
            if result:
                download_status[download_id] = {'status': 'completed', 'file': result}
            else:
                download_status[download_id] = {'status': 'error', 'message': 'Download failed - no file returned'}
        except Exception as e:
            download_status[download_id] = {'status': 'error', 'message': str(e)}
    
    thread = threading.Thread(target=download_task)
    thread.start()
    
    return jsonify({'download_id': download_id})

@app.route('/status/<download_id>')
def status(download_id):
    return jsonify(download_status.get(download_id, {'status': 'not_found'}))

@app.route('/search-username', methods=['POST'])
def search_username():
    data = request.json
    username = data.get('username', '').strip()
    
    if not username:
        return jsonify({'error': 'Username required'}), 400
    
    if len(username) < 2 or len(username) > 30:
        return jsonify({'error': 'Username must be 2-30 characters'}), 400
    
    # Search username across platforms
    results = username_checker.search_username(username)
    
    return jsonify(results)

@app.route('/file/<path:filename>')
def download_file(filename):
    filepath = os.path.join(app.config['DOWNLOAD_FOLDER'], filename)
    if os.path.exists(filepath):
        # Detect MIME type for proper preview
        import mimetypes
        mimetype = mimetypes.guess_type(filepath)[0]
        
        # For video files, use inline display instead of attachment
        if mimetype and mimetype.startswith('video'):
            return send_file(filepath, mimetype=mimetype)
        else:
            return send_file(filepath, as_attachment=True)
    else:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    # Auto proxy updater disabled for stability
    # Uncomment below to enable:
    # start_auto_updater(interval_hours=6)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
