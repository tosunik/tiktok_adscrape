import re
import json
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from loguru import logger

class EnhancedTikTokVideoExtractor:
    """TikTok Ad Library'den gerçek video URL'lerini çıkarma"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def extract_video_urls_advanced(self, ad_element, index: int) -> dict:
        """Gelişmiş video URL çıkarma yöntemleri"""
        video_data = {
            'media_urls': [],
            'media_type': 'text',
            'video_found': False,
            'extraction_method': None
        }
        
        # Yöntem 1: Reklam detay sayfasına git
        video_urls = self._method_1_detail_page(ad_element, index)
        if video_urls:
            video_data.update(video_urls)
            return video_data
        
        # Yöntem 2: Network isteklerini yakala
        video_urls = self._method_2_network_capture(ad_element)
        if video_urls:
            video_data.update(video_urls)
            return video_data
        
        # Yöntem 3: JavaScript execution
        video_urls = self._method_3_javascript_execution(ad_element)
        if video_urls:
            video_data.update(video_urls)
            return video_data
        
        # Yöntem 4: Alternatif selector'lar
        video_urls = self._method_4_alternative_selectors(ad_element)
        if video_urls:
            video_data.update(video_urls)
            return video_data
        
        return video_data
    
    def _method_1_detail_page(self, ad_element, index: int) -> dict:
        """Yöntem 1: Reklam detay sayfasına giderek video URL'i bul"""
        try:
            # Reklam linkini bul
            link_elem = ad_element.find_element(By.CSS_SELECTOR, 'a[href*="detail"]')
            detail_url = link_elem.get_attribute('href')
            
            if not detail_url:
                return None
            
            logger.info(f"Detay sayfasına gidiliyor: {detail_url}")
            
            # Yeni tab'da aç
            self.driver.execute_script("window.open(arguments[0], '_blank');", detail_url)
            
            # Yeni tab'a geç
            self.driver.switch_to.window(self.driver.window_handles[-1])
            
            # Sayfa yüklensin
            time.sleep(5)
            
            # Video player'ı bul
            video_urls = self._extract_from_detail_page()
            
            # Tab'ı kapat ve ana tab'a dön
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
            return video_urls
            
        except Exception as e:
            logger.debug(f"Method 1 failed: {e}")
            return None
    
    def _extract_from_detail_page(self) -> dict:
        """Detay sayfasından video URL çıkar"""
        try:
            # Video elementi bekle
            video_selectors = [
                'video source',
                'video',
                '[src*=".mp4"]',
                '[src*=".mov"]',
                '[data-video-src]',
                '.video-player video'
            ]
            
            for selector in video_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        src = elem.get_attribute('src') or elem.get_attribute('data-src')
                        if src and any(ext in src.lower() for ext in ['.mp4', '.mov', '.avi']):
                            return {
                                'media_urls': [src],
                                'media_type': 'video',
                                'video_found': True,
                                'extraction_method': 'detail_page'
                            }
                except:
                    continue
            
            # Page source'da video URL ara
            page_source = self.driver.page_source
            video_urls = re.findall(r'https://[^"\']*\.mp4[^"\']*', page_source)
            if video_urls:
                return {
                    'media_urls': video_urls,
                    'media_type': 'video', 
                    'video_found': True,
                    'extraction_method': 'detail_page_regex'
                }
                
        except Exception as e:
            logger.debug(f"Detail page extraction failed: {e}")
        
        return None
    
    def _method_2_network_capture(self, ad_element) -> dict:
        """Yöntem 2: Browser network logs'undan video URL yakala"""
        try:
            # Chrome DevTools Protocol kullanarak network logları al
            logs = self.driver.get_log('performance')
            
            for log in logs:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    url = message['message']['params']['response']['url']
                    if any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi']) and 'tiktok' in url:
                        return {
                            'media_urls': [url],
                            'media_type': 'video',
                            'video_found': True,
                            'extraction_method': 'network_logs'
                        }
        except Exception as e:
            logger.debug(f"Method 2 failed: {e}")
        
        return None
    
    def _method_3_javascript_execution(self, ad_element) -> dict:
        """Yöntem 3: JavaScript ile video elementi bul"""
        try:
            # JavaScript ile video URL'lerini ara
            js_code = """
            let videoUrls = [];
            
            // Tüm video elementlerini bul
            document.querySelectorAll('video, [src*=".mp4"], [data-video-src]').forEach(el => {
                let src = el.src || el.getAttribute('data-video-src') || el.getAttribute('data-src');
                if (src && src.includes('.mp4')) {
                    videoUrls.push(src);
                }
            });
            
            // TikTok CDN URL'lerini page source'da ara
            let pageText = document.documentElement.innerHTML;
            let matches = pageText.match(/https:\/\/[^"']*\.mp4[^"']*/g);
            if (matches) {
                videoUrls = videoUrls.concat(matches);
            }
            
            return [...new Set(videoUrls)]; // Duplicates'i kaldır
            """
            
            video_urls = self.driver.execute_script(js_code)
            
            if video_urls:
                return {
                    'media_urls': video_urls,
                    'media_type': 'video',
                    'video_found': True,
                    'extraction_method': 'javascript'
                }
                
        except Exception as e:
            logger.debug(f"Method 3 failed: {e}")
        
        return None
    
    def _method_4_alternative_selectors(self, ad_element) -> dict:
        """Yöntem 4: Alternatif CSS selector'ları dene"""
        try:
            alternative_selectors = [
                # TikTok spesifik selector'lar
                '[class*="video"]',
                '[class*="player"]',
                '[data-testid*="video"]',
                'source',
                '[type="video/mp4"]',
                
                # Data attribute'ları
                '[data-video-url]',
                '[data-src*=".mp4"]',
                '[data-video-src]',
                
                # Background image'dan gerçek video çıkarma
                '.video_player',
                '.video-container',
                '.video-wrapper'
            ]
            
            for selector in alternative_selectors:
                try:
                    elements = ad_element.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        # Farklı attribute'ları kontrol et
                        for attr in ['src', 'data-src', 'data-video-src', 'data-video-url', 'href']:
                            url = elem.get_attribute(attr)
                            if url and any(ext in url.lower() for ext in ['.mp4', '.mov', '.avi']):
                                return {
                                    'media_urls': [url],
                                    'media_type': 'video',
                                    'video_found': True,
                                    'extraction_method': f'alternative_selector_{selector}'
                                }
                except:
                    continue
                    
        except Exception as e:
            logger.debug(f"Method 4 failed: {e}")
        
        return None
    
    def download_video_with_headers(self, video_url: str, filename: str) -> bool:
        """TikTok uyumlu header'larla video indir"""
        try:
            import requests
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://library.tiktok.com/',
                'Accept': 'video/webm,video/ogg,video/*;q=0.9,application/ogg;q=0.7,audio/*;q=0.6,*/*;q=0.5',
                'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'video',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site'
            }
            
            response = requests.get(video_url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()
            
            # Content-Type kontrolü
            content_type = response.headers.get('Content-Type', '').lower()
            if 'video' not in content_type and 'octet-stream' not in content_type:
                logger.warning(f"Unexpected content type: {content_type}")
                return False
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # Dosya boyut kontrolü
            import os
            file_size = os.path.getsize(filename)
            if file_size < 1024:  # 1KB'den küçükse muhtemelen error
                logger.warning(f"Downloaded file too small: {file_size} bytes")
                return False
            
            logger.info(f"Video downloaded successfully: {filename} ({file_size} bytes)")
            return True
            
        except Exception as e:
            logger.error(f"Video download failed: {e}")
            return False