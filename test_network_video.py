#!/usr/bin/env python3
"""
Advanced Network Video Extraction Test
"""

import sys
import os
from pathlib import Path
# NetworkVideoExtractor'ı tiktok_selenium_scraper.py dosyasından import et
import importlib.util
import sys

# Scraper modülünü yeniden yükle (NetworkVideoExtractor class'ı ekledikten sonra)
spec = importlib.util.spec_from_file_location("tiktok_selenium_scraper", 
                                              "src/scraper/tiktok_selenium_scraper.py")
scraper_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scraper_module)

NetworkVideoExtractor = scraper_module.NetworkVideoExtractor

# Proje path'ini ayarla
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.scraper.tiktok_selenium_scraper import TikTokSeleniumScraper
from selenium.webdriver.common.by import By
import time
import json
from loguru import logger

def test_advanced_video_extraction():
    """Gelişmiş video extraction test"""
    
    logger.info("🚀 Advanced Video Extraction Test Başlatılıyor...")
    
    # Scraper'ı oluştur (headless=False debug için)
    scraper = TikTokSeleniumScraper(headless=False)
    
    if not scraper.setup_driver():
        logger.error("❌ WebDriver kurulamadı")
        return
    
    try:
        # Test URL - Garanti reklamları
        test_url = "https://library.tiktok.com/ads?region=TR&adv_name=garanti"
        logger.info(f"🔗 Test URL'e gidiliyor: {test_url}")
        
        scraper.driver.get(test_url)
        time.sleep(8)  # Sayfa tam yüklensin
        
        # Reklam kartlarını bul
        ad_cards = scraper.driver.find_elements(By.CSS_SELECTOR, '.ad_card')
        logger.info(f"📋 {len(ad_cards)} reklam kartı bulundu")
        
        if not ad_cards:
            logger.error("❌ Reklam kartı bulunamadı!")
            return
        
        # NetworkVideoExtractor'ı import et (dynamic import)
        # Kendi dosyanızdan import edin
        from src.scraper.tiktok_selenium_scraper import NetworkVideoExtractor
        
        video_extractor = NetworkVideoExtractor(scraper.driver)
        
        # İlk 3 reklam kartını test et
        for i, ad_card in enumerate(ad_cards[:3], 1):
            logger.info(f"\n🎯 Reklam {i} test ediliyor...")
            
            try:
                # Advertiser name
                try:
                    advertiser_elem = ad_card.find_element(By.CSS_SELECTOR, '.ad_info_text')
                    advertiser_name = advertiser_elem.text.strip()
                    logger.info(f"📢 Advertiser: {advertiser_name}")
                except:
                    advertiser_name = "Unknown"
                    logger.warning("⚠️ Advertiser name bulunamadı")
                
                # Detay sayfası video extraction test
                video_url = video_extractor.extract_video_from_detail_page(ad_card, max_wait=12)
                
                if video_url:
                    logger.info(f"✅ SUCCESS! Video URL bulundu")
                    logger.info(f"🎬 URL: {video_url}")
                    
                    # Video URL'i validate et
                    validate_video_url(video_url)
                    
                    # İlk başarılı videoyu bulduktan sonra dur
                    logger.info("✅ Video extraction başarılı! Test tamamlandı.")
                    break
                    
                else:
                    logger.warning(f"⚠️ Reklam {i} için video bulunamadı")
                    
                    # Fallback: Ana sayfada thumbnail test
                    test_thumbnail_extraction(ad_card)
            
            except Exception as e:
                logger.error(f"❌ Reklam {i} test hatası: {e}")
                continue
        
        else:
            logger.warning("⚠️ Hiçbir reklamdan video URL çıkarılamadı")
        
        # Network activity summary
        summarize_network_activity(scraper.driver)
        
    except Exception as e:
        logger.error(f"❌ Test sırasında genel hata: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Manual inspection
        input("\n🔍 Manuel inceleme için Enter'a basın...")
        scraper.close_driver()
        logger.info("✅ Test tamamlandı")

def test_thumbnail_extraction(ad_card):
    """Fallback thumbnail extraction test"""
    try:
        logger.info("📸 Thumbnail extraction test...")
        
        video_player = ad_card.find_element(By.CSS_SELECTOR, '.video_player')
        style = video_player.get_attribute('style')
        
        if style and 'background-image' in style:
            import re
            url_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
            if url_match:
                thumbnail_url = url_match.group(1)
                logger.info(f"📸 Thumbnail URL: {thumbnail_url[:100]}...")
                return thumbnail_url
        
        return None
        
    except Exception as e:
        logger.debug(f"Thumbnail extraction hatası: {e}")
        return None

def validate_video_url(video_url: str):
    """Video URL'ini validate et"""
    try:
        import requests
        
        logger.info(f"🔍 Video URL validasyonu...")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://library.tiktok.com/',
            'Accept': 'video/webm,video/ogg,video/*;q=0.9,*/*;q=0.5',
            'Range': 'bytes=0-1023'  # Sadece ilk 1KB'yi indir
        }
        
        response = requests.get(video_url, headers=headers, timeout=15, stream=True)
        
        logger.info(f"📊 HTTP Status: {response.status_code}")
        logger.info(f"📋 Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
        logger.info(f"📏 Content-Length: {response.headers.get('Content-Length', 'Unknown')} bytes")
        
        # Content type kontrolü
        content_type = response.headers.get('Content-Type', '').lower()
        
        if 'video' in content_type:
            logger.info("✅ BAŞARILI! Bu gerçek bir video dosyası")
            
            # İlk chunk'ı al ve magic number kontrol et
            first_chunk = next(response.iter_content(chunk_size=1024))
            logger.info(f"📁 İlk chunk boyutu: {len(first_chunk)} bytes")
            
            # Video magic number kontrolü
            if first_chunk.startswith(b'\x00\x00\x00') or b'ftyp' in first_chunk[:32]:
                logger.info("✅ Video magic number doğrulandı!")
                return True
            else:
                logger.warning("⚠️ Video magic number bulunamadı")
                
        elif 'image' in content_type:
            logger.warning("⚠️ Bu bir resim dosyası (thumbnail)")
            return False
        else:
            logger.warning(f"❓ Bilinmeyen content type: {content_type}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Video validation hatası: {e}")
        return False

def summarize_network_activity(driver):
    """Network aktivitesini özetle"""
    try:
        logger.info("\n📊 Network Activity Summary...")
        
        logs = driver.get_log('performance')
        
        network_events = {}
        video_related = 0
        
        for log in logs:
            try:
                message = json.loads(log['message'])
                method = message.get('message', {}).get('method', '')
                
                if 'Network.' in method:
                    network_events[method] = network_events.get(method, 0) + 1
                    
                    # Video related events
                    if 'params' in message.get('message', {}):
                        params = message['message']['params']
                        
                        # Response events
                        if 'response' in params:
                            url = params['response'].get('url', '')
                            mime_type = params['response'].get('mimeType', '')
                            
                            if any(keyword in url.lower() + mime_type.lower() for keyword in ['video', 'mp4', 'tiktok']):
                                video_related += 1
                        
                        # Request events
                        elif 'request' in params:
                            url = params['request'].get('url', '')
                            
                            if any(keyword in url.lower() for keyword in ['video', 'mp4', 'tiktok']):
                                video_related += 1
                                
            except:
                continue
        
        logger.info(f"📡 Toplam network event: {len(logs)}")
        logger.info(f"🎬 Video related event: {video_related}")
        
        # Top network events
        sorted_events = sorted(network_events.items(), key=lambda x: x[1], reverse=True)[:5]
        logger.info("🔝 En sık network eventler:")
        for event, count in sorted_events:
            logger.info(f"   {event}: {count}")
            
    except Exception as e:
        logger.error(f"Network summary hatası: {e}")

if __name__ == "__main__":
    test_advanced_video_extraction()