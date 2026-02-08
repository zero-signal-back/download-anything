import schedule
import time
from proxy_scraper import ProxyScraper
import threading

def update_proxies():
    print("\n" + "="*50)
    print("🔄 Auto-updating proxy list...")
    print("="*50)
    
    scraper = ProxyScraper()
    proxies = scraper.scrape_proxies(test=True, max_test=100)
    
    if proxies:
        scraper.save_proxies(proxies)
        print("✅ Proxy list updated!")
    else:
        print("⚠️ No working proxies found")
    
    print("="*50 + "\n")

def start_auto_updater(interval_hours=6):
    """Start background proxy updater"""
    # Update immediately on start
    update_proxies()
    
    # Schedule periodic updates
    schedule.every(interval_hours).hours.do(update_proxies)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    print(f"🤖 Auto-updater started (updates every {interval_hours} hours)")

if __name__ == '__main__':
    print("🚀 Starting Proxy Auto-Updater")
    print("This will update proxies every 6 hours")
    print("Press Ctrl+C to stop\n")
    
    start_auto_updater(interval_hours=6)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Proxy updater stopped")
