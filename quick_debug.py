from src.scraper.tiktok_selenium_scraper import TikTokSeleniumScraper
from selenium.webdriver.common.by import By
import time

scraper = TikTokSeleniumScraper(headless=False)
scraper.setup_driver()

url = "https://library.tiktok.com/ads?region=TR&adv_name=akbank"
scraper.driver.get(url)
time.sleep(10)

ad_cards = scraper.driver.find_elements(By.CSS_SELECTOR, '.ad_card')
if ad_cards:
    card = ad_cards[0]
    print("=== EXTRACTION DEBUG ===")
    print(f"Card text: {card.text[:200]}")
    
    # Test all possible selectors
    selectors = ['.ad_info_text', '.advertiser', '[class*="advertiser"]', 'h3', 'h4', '.ad_detail', '.info']
    
    for selector in selectors:
        try:
            elem = card.find_element(By.CSS_SELECTOR, selector)
            print(f"✅ {selector}: {elem.text[:50]}")
        except:
            print(f"❌ {selector}: Not found")

scraper.close_driver()