import os
import re

# Mobile menu CSS
mobile_css = '''
        .mobile-menu-btn {
            display: none;
            background: none;
            border: none;
            color: white;
            font-size: 24px;
            cursor: pointer;
        }
        
        .nav-links {
            display: flex;
            gap: 20px;
        }
        
        @media (max-width: 768px) {
            .mobile-menu-btn {
                display: block;
            }
            
            .nav-links {
                display: none;
                position: absolute;
                top: 60px;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                flex-direction: column;
                padding: 20px;
                gap: 15px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            .nav-links.active {
                display: flex;
            }
        }
'''

# Toggle function
toggle_script = '''
    <script>
        function toggleMenu() {
            document.getElementById('navLinks').classList.toggle('active');
        }
    </script>'''

files = ['index.html', 'username.html', 'adult_downloader.html']

for filename in files:
    filepath = f'templates/{filename}'
    if not os.path.exists(filepath):
        continue
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add mobile CSS if not present
    if '.mobile-menu-btn' not in content:
        content = re.sub(r'<style>', f'<style>{mobile_css}', content, count=1)
    
    # Add hamburger button and nav-links class
    if 'mobile-menu-btn' not in content:
        # Replace nav structure
        old_nav = r'<div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; flex-wrap: wrap; gap: 10px;">'
        new_nav = '<div style="max-width: 1200px; margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 0 20px; position: relative;">'
        content = content.replace(old_nav, new_nav)
        
        # Add hamburger button after logo
        content = re.sub(
            r'(</a>\s*<div style="display: flex; gap: \d+px;)',
            r'</a>\n            <button class="mobile-menu-btn" onclick="toggleMenu()">\n                <i class="fas fa-bars"></i>\n            </button>\n            <div class="nav-links" id="navLinks" style="display: flex; gap: 20px;',
            content
        )
        
        # Add toggle script before </body>
        if 'function toggleMenu()' not in content:
            content = content.replace('</body>', f'{toggle_script}\n</body>')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f'Updated: {filename}')

print('All main pages updated with hamburger menu!')
