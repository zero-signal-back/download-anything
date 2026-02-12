import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import socket

class ProxyScraper:
    def __init__(self):
        self.sources = [
            'https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all',
            'https://www.proxy-list.download/api/v1/get?type=http',
            'https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt',
            'https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt',
            'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt',
            'https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt',
        ]
        
    def fetch_from_source(self, url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                proxies = re.findall(r'\d+\.\d+\.\d+\.\d+:\d+', response.text)
                return proxies
        except:
            pass
        return []
    
    def test_proxy(self, proxy, timeout=3):
        try:
            test_url = 'http://www.google.com'
            proxies = {
                'http': f'http://{proxy}',
                'https': f'http://{proxy}'
            }
            response = requests.get(test_url, proxies=proxies, timeout=timeout)
            return proxy if response.status_code == 200 else None
        except:
            return None
    
    def scrape_proxies(self, test=True, max_test=50):
        print("🔍 Fetching proxies from multiple sources...")
        all_proxies = []
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            results = executor.map(self.fetch_from_source, self.sources)
            for result in results:
                all_proxies.extend(result)
        
        all_proxies = list(set(all_proxies))
        print(f"✅ Found {len(all_proxies)} unique proxies")
        
        if test and all_proxies:
            print(f"🧪 Testing proxies (max {max_test})...")
            working_proxies = []
            test_proxies = all_proxies[:max_test]
            
            with ThreadPoolExecutor(max_workers=30) as executor:
                future_to_proxy = {executor.submit(self.test_proxy, proxy): proxy for proxy in test_proxies}
                for future in as_completed(future_to_proxy):
                    result = future.result()
                    if result:
                        working_proxies.append(result)
                        print(f"✓ Working: {result}")
            
            print(f"✅ {len(working_proxies)} working proxies found")
            return working_proxies if working_proxies else [None]
        
        return all_proxies if all_proxies else [None]
    
    def save_proxies(self, proxies, filename='proxies.txt'):
        with open(filename, 'w') as f:
            f.write("# Auto-generated proxy list\n")
            f.write(f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total proxies: {len(proxies)}\n\n")
            for proxy in proxies:
                f.write(f"http://{proxy}\n")
        print(f"💾 Saved {len(proxies)} proxies to {filename}")

def main():
    scraper = ProxyScraper()
    proxies = scraper.scrape_proxies(test=True, max_test=100)
    
    if proxies and proxies != [None]:
        scraper.save_proxies(proxies)
        print("\n✅ Proxy list updated successfully!")
    else:
        print("\n⚠️ No working proxies found. Using direct connection.")
        with open('proxies.txt', 'w') as f:
            f.write("# No proxies available - using direct connection\n")

if __name__ == '__main__':
    main()
