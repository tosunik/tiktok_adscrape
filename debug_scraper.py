from src.scraper.tiktok_selenium_scraper import TikTokSeleniumScraper
from src.config.settings import settings
import time

def debug_tiktok_page():
    scraper = TikTokSeleniumScraper(headless=False)  # Headless=False: Tarayıcıyı görürüz
    
    if scraper.setup_driver():
        try:
            # Garanti reklamlarını ara
            url = scraper.build_search_url("garanti")
            print(f"URL: {url}")
            
            scraper.driver.get(url)
            time.sleep(10)  # Sayfa tam yüklensin
            
            # Screenshot al
            scraper.save_screenshot("debug_screenshot.png")
            
            # Console'da dur (manuel inceleme için)
            input("Tarayıcıyı manuel olarak incele, sonra Enter'a bas...")
            
            # Sayfa HTML'ini kaydet
            with open("debug_page_source.html", "w", encoding="utf-8") as f:
                f.write(scraper.driver.page_source)
            
            print("Debug dosyaları kaydedildi:")
            print("- debug_screenshot.png")
            print("- debug_page_source.html")
            
        finally:
            scraper.close_driver()

if __name__ == "__main__":
    debug_tiktok_page()