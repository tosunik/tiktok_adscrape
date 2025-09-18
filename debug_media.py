from src.scraper.tiktok_selenium_scraper import TikTokSeleniumScraper
from selenium.webdriver.common.by import By
import time
import re

scraper = TikTokSeleniumScraper(headless=False)
scraper.setup_driver()

url = "https://library.tiktok.com/ads?region=TR&adv_name=garanti"
scraper.driver.get(url)
time.sleep(10)

# İlk reklam kartını al
ad_cards = scraper.driver.find_elements(By.CSS_SELECTOR, '.ad_card')
if ad_cards:
    first_card = ad_cards[0]
    
    print("=== MEDIA URL DEBUG ===")
    
    # 1. Video player check
    try:
        video_player = first_card.find_element(By.CSS_SELECTOR, '.video_player')
        style = video_player.get_attribute('style')
        print(f"Video player style: {style}")
        
        if style and 'background-image' in style:
            url_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
            if url_match:
                print(f"Video URL found: {url_match.group(1)}")
    except Exception as e:
        print(f"Video player not found: {e}")
    
    # 2. Image elements check
    try:
        images = first_card.find_elements(By.CSS_SELECTOR, 'img')
        print(f"Found {len(images)} image elements")
        
        for i, img in enumerate(images):
            src = img.get_attribute('src')
            print(f"Image {i}: {src}")
    except Exception as e:
        print(f"Images not found: {e}")
    
    # 3. All elements with URLs
    try:
        all_elements = first_card.find_elements(By.CSS_SELECTOR, '*')
        urls_found = []
        
        for element in all_elements:
            # Background images
            style = element.get_attribute('style')
            if style and 'url(' in style:
                urls_found.append(f"Style URL: {style}")
            
            # Src attributes  
            src = element.get_attribute('src')
            if src and src.startswith('http'):
                urls_found.append(f"Src URL: {src}")
                
            # Data attributes
            for attr in ['data-src', 'data-url', 'data-video-src']:
                data_attr = element.get_attribute(attr)
                if data_attr:
                    urls_found.append(f"{attr}: {data_attr}")
        
        print(f"\nAll URLs found: {len(urls_found)}")
        for url in urls_found[:10]:  # İlk 10'unu göster
            print(f"  {url}")
            
    except Exception as e:
        print(f"URL search error: {e}")

scraper.close_driver()