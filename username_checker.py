import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class UsernameChecker:
    def __init__(self):
        self.platforms = {
            # Social Media
            "Instagram": "https://www.instagram.com/{}",
            "Twitter": "https://twitter.com/{}",
            "Facebook": "https://www.facebook.com/{}",
            "TikTok": "https://www.tiktok.com/@{}",
            "YouTube": "https://www.youtube.com/@{}",
            "LinkedIn": "https://www.linkedin.com/in/{}",
            "Snapchat": "https://www.snapchat.com/add/{}",
            "Pinterest": "https://www.pinterest.com/{}",
            "Reddit": "https://www.reddit.com/user/{}",
            "Tumblr": "https://{}.tumblr.com",
            "Medium": "https://medium.com/@{}",
            "Twitch": "https://www.twitch.tv/{}",
            "Vimeo": "https://vimeo.com/{}",
            "Dailymotion": "https://www.dailymotion.com/{}",
            "Flickr": "https://www.flickr.com/people/{}",
            "DeviantArt": "https://www.deviantart.com/{}",
            "Behance": "https://www.behance.net/{}",
            "Dribbble": "https://dribbble.com/{}",
            "SoundCloud": "https://soundcloud.com/{}",
            "Spotify": "https://open.spotify.com/user/{}",
            "Patreon": "https://www.patreon.com/{}",
            "OnlyFans": "https://onlyfans.com/{}",
            
            # Developer Platforms
            "GitHub": "https://github.com/{}",
            "GitLab": "https://gitlab.com/{}",
            "Bitbucket": "https://bitbucket.org/{}",
            "Stack Overflow": "https://stackoverflow.com/users/{}",
            "CodePen": "https://codepen.io/{}",
            "Replit": "https://replit.com/@{}",
            "HackerRank": "https://www.hackerrank.com/{}",
            "LeetCode": "https://leetcode.com/{}",
            
            # Gaming
            "Steam": "https://steamcommunity.com/id/{}",
            "Xbox": "https://account.xbox.com/en-us/profile?gamertag={}",
            "PlayStation": "https://psnprofiles.com/{}",
            "Roblox": "https://www.roblox.com/users/profile?username={}",
            "Minecraft": "https://namemc.com/profile/{}",
            "Discord": "https://discord.com/users/{}",
            
            # Indian Platforms
            "ShareChat": "https://sharechat.com/profile/{}",
            "Moj": "https://mojapp.in/@{}",
            "Josh": "https://share.josh.in/profile/{}",
            "Roposo": "https://www.roposo.com/@{}",
            "Chingari": "https://chingari.io/{}",
            
            # Professional
            "AngelList": "https://angel.co/u/{}",
            "Crunchbase": "https://www.crunchbase.com/person/{}",
            "About.me": "https://about.me/{}",
            "Linktree": "https://linktr.ee/{}",
            
            # Forums & Communities
            "Quora": "https://www.quora.com/profile/{}",
            "9GAG": "https://9gag.com/u/{}",
            "Imgur": "https://imgur.com/user/{}",
            "ProductHunt": "https://www.producthunt.com/@{}",
            "Hacker News": "https://news.ycombinator.com/user?id={}",
            
            # Dating & Social
            "Tinder": "https://www.gotinder.com/@{}",
            "Bumble": "https://bumble.com/{}",
            "OkCupid": "https://www.okcupid.com/profile/{}",
            
            # Content Platforms
            "Substack": "https://{}.substack.com",
            "Wattpad": "https://www.wattpad.com/user/{}",
            "Goodreads": "https://www.goodreads.com/{}",
            "Letterboxd": "https://letterboxd.com/{}",
            
            # Others
            "Telegram": "https://t.me/{}",
            "WhatsApp": "https://wa.me/{}",
            "Clubhouse": "https://www.clubhouse.com/@{}",
            "Mastodon": "https://mastodon.social/@{}",
            "Kick": "https://kick.com/{}",
            "Rumble": "https://rumble.com/user/{}",
        }
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def check_platform(self, platform_name, url, timeout=5):
        try:
            response = requests.get(url, headers=self.headers, timeout=timeout, allow_redirects=True)
            
            # Check if profile exists based on status code and content
            if response.status_code == 200:
                content_lower = response.text.lower()
                
                # Platform-specific checks
                if "instagram.com" in url:
                    if "page not found" in content_lower or "sorry, this page" in content_lower:
                        return None
                elif "twitter.com" in url or "x.com" in url:
                    if "this account doesn't exist" in content_lower or "account suspended" in content_lower:
                        return None
                elif "github.com" in url:
                    if "404" in content_lower or "not found" in content_lower:
                        return None
                elif "facebook.com" in url:
                    if "content not found" in content_lower or "page not found" in content_lower:
                        return None
                elif "tiktok.com" in url:
                    if "couldn't find this account" in content_lower:
                        return None
                elif "reddit.com" in url:
                    if "page not found" in content_lower or "nobody on reddit" in content_lower:
                        return None
                    
                return {
                    'platform': platform_name,
                    'url': url,
                    'status': 'found',
                    'status_code': response.status_code
                }
            else:
                return None
                
        except requests.exceptions.Timeout:
            return None
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None
    
    def search_username(self, username, max_workers=20):
        results = {
            'username': username,
            'found': [],
            'total_checked': len(self.platforms),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {}
            
            for platform_name, url_template in self.platforms.items():
                url = url_template.format(username)
                future = executor.submit(self.check_platform, platform_name, url)
                futures[future] = platform_name
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results['found'].append(result)
        
        # Sort by platform name
        results['found'].sort(key=lambda x: x['platform'])
        results['found_count'] = len(results['found'])
        
        return results
