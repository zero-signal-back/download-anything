import os
import re

# Navbar HTML
navbar = '''<nav style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 15px 0; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: fixed; top: 0; left: 0; right: 0; z-index: 1000;">
        <div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; flex-wrap: wrap; gap: 10px;">
            <a href="/" style="color: white; text-decoration: none; font-weight: 600; font-size: clamp(16px, 3vw, 20px);">
                <i class="fas fa-download"></i> Download Anything
            </a>
            <div style="display: flex; gap: 15px; flex-wrap: wrap;">
                <a href="/" style="color: white; text-decoration: none; font-weight: 500; font-size: clamp(13px, 2.5vw, 15px); transition: opacity 0.3s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                    <i class="fas fa-home"></i> Home
                </a>
                <a href="/adult-downloader" style="color: white; text-decoration: none; font-weight: 500; font-size: clamp(13px, 2.5vw, 15px); transition: opacity 0.3s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                    <i class="fas fa-fire"></i> Adult
                </a>
                <a href="/username-finder" style="color: white; text-decoration: none; font-weight: 500; font-size: clamp(13px, 2.5vw, 15px); transition: opacity 0.3s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                    <i class="fas fa-search"></i> Username
                </a>
                <a href="/do-anything" style="color: white; text-decoration: none; font-weight: 500; font-size: clamp(13px, 2.5vw, 15px); transition: opacity 0.3s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                    <i class="fas fa-magic"></i> Tools
                </a>
            </div>
        </div>
    </nav>
    <div style="height: 80px;"></div>'''

# CSS to add
responsive_css = '''
        * { box-sizing: border-box; }
        body { margin: 0; padding: 0; min-height: 100vh; }
        .tool-container { max-width: 700px; width: 95%; margin: 40px auto; padding: 20px; background: white; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }
        .tool-header { text-align: center; margin-bottom: 30px; }
        .tool-header h1 { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: clamp(24px, 5vw, 36px); margin-bottom: 10px; word-wrap: break-word; }
        .upload-box { border: 3px dashed #f5576c; border-radius: 15px; padding: 30px 15px; text-align: center; cursor: pointer; transition: all 0.3s; background: rgba(245, 87, 108, 0.05); }
        .upload-box:hover { background: rgba(245, 87, 108, 0.1); border-color: #f093fb; }
        .upload-box input { display: none; }
        .upload-icon { font-size: clamp(40px, 10vw, 60px); color: #f5576c; margin-bottom: 15px; }
        .upload-box h3 { font-size: clamp(16px, 3vw, 20px); word-wrap: break-word; }
        .options-panel { margin-top: 25px; display: none; }
        .options-panel.active { display: block; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; font-size: clamp(14px, 2.5vw, 16px); }
        .form-group select, .form-group input, .form-group textarea { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 10px; font-size: clamp(14px, 2.5vw, 15px); transition: border 0.3s; }
        .form-group select:focus, .form-group input:focus, .form-group textarea:focus { outline: none; border-color: #f5576c; }
        .process-button { width: 100%; padding: 15px; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; border: none; border-radius: 10px; font-size: clamp(16px, 3vw, 18px); font-weight: 600; cursor: pointer; transition: all 0.3s; margin-top: 20px; }
        .process-button:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(245, 87, 108, 0.4); }
        .process-button:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
        .status-box { margin-top: 20px; padding: 15px; border-radius: 10px; display: none; word-wrap: break-word; font-size: clamp(14px, 2.5vw, 16px); }
        .status-box.active { display: block; }
        .status-box.processing { background: #fff3cd; color: #856404; }
        .status-box.success { background: #d4edda; color: #155724; }
        .status-box.error { background: #f8d7da; color: #721c24; }
        .download-btn { display: inline-block; margin-top: 15px; padding: 12px 30px; background: #28a745; color: white; text-decoration: none; border-radius: 10px; font-weight: 600; font-size: clamp(14px, 2.5vw, 16px); cursor: pointer; border: none; }
        .download-btn:hover { background: #218838; }
        .back-link { display: inline-block; margin-bottom: 20px; color: #f5576c; text-decoration: none; font-weight: 600; font-size: clamp(14px, 2.5vw, 16px); }
        @media (max-width: 768px) {
            .tool-container { margin: 20px auto; padding: 15px; }
            .upload-box { padding: 20px 10px; }
            .form-group { margin-bottom: 15px; }
        }'''

tool_files = [
    'tool_gif.html', 'tool_compress.html', 'tool_convert.html', 
    'tool_rotate.html', 'tool_thumbnail.html', 'tool_subtitle.html',
    'tool_pdf.html', 'tool_qr.html'
]

for filename in tool_files:
    filepath = f'templates/{filename}'
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add responsive CSS if not present
    if '* { box-sizing: border-box; }' not in content:
        content = re.sub(r'<style>', f'<style>{responsive_css}', content, count=1)
    
    # Add navbar if not present
    if '<nav style=' not in content:
        content = re.sub(r'<body>', f'<body>\n    {navbar}\n    <script async="async" data-cfasync="false" src="//breachuptown.com/6f/78/04/6f780474eb2a9dd7858efa9f1093bfff.js"></script>', content, count=1)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Updated: {filename}')

print('All tool pages updated!')
