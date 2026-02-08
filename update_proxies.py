"""
Manual Proxy Updater
Run this script anytime to manually update your proxy list
"""

from proxy_scraper import ProxyScraper

if __name__ == '__main__':
    print("🚀 Manual Proxy Update")
    print("="*50)
    
    scraper = ProxyScraper()
    
    # Fetch proxies
    proxies = scraper.scrape_proxies(test=True, max_test=100)
    
    if proxies:
        scraper.save_proxies(proxies)
        print(f"\n✅ SUCCESS! {len(proxies)} working proxies saved to proxies.txt")
    else:
        print("\n❌ No working proxies found")
        print("Try running again or check your internet connection")
    
    print("="*50)
