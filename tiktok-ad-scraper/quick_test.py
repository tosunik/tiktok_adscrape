from src.scraper.tiktok_selenium_scraper import TikTokSeleniumScraper
from selenium.webdriver.common.by import By
import time

scraper = TikTokSeleniumScraper(headless=False)
scraper.setup_driver()

url = "https://library.tiktok.com/ads?region=TR&adv_name=garanti"
scraper.driver.get(url)
time.sleep(10)

# Test real selectors
ad_cards = scraper.driver.find_elements(By.CSS_SELECTOR, '.ad_card')
print(f"Found .ad_card elements: {len(ad_cards)}")

if ad_cards:
    first_card = ad_cards[0]
    try:
        advertiser = first_card.find_element(By.CSS_SELECTOR, '.ad_info_text')
        print(f"Advertiser: {advertiser.text}")
    except:
        print("Advertiser not found in .ad_info_text")
        
        # All text in first card
        print(f"All text: {first_card.text[:200]}")

scraper.close_driver()