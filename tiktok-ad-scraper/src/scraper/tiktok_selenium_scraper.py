# tiktok_selenium_scraper.py dosyanızın başındaki import'ları bu şekilde güncelleyin:

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
# Bu satırı KALDIR - artık gerekli değil: from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from loguru import logger

from src.config.settings import settings
from src.utils.helpers import safe_sleep, clean_text

from src.config.settings import settings
from src.utils.helpers import safe_sleep, clean_text
class NetworkVideoExtractor:
    """Network requests'lerden video URL'lerini yakalama"""
    
    def __init__(self, driver):
        self.driver = driver
        self.captured_video_urls = []
        self.network_logs = []
    
    def start_network_monitoring(self):
        """Network monitoring başlat"""
        try:
            # Mevcut network logs'u temizle
            self.driver.get_log('performance')
            logger.info("Network monitoring başlatıldı")
        except Exception as e:
            logger.warning(f"Network monitoring başlatılamadı: {e}")
    
    def capture_network_requests(self, duration_seconds: int = 10) -> List[str]:
        """Network isteklerini yakala ve video URL'lerini filtrele"""
        video_urls = []
        
        try:
            # Belirli süre boyunca network isteklerini topla
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                logs = self.driver.get_log('performance')
                
                for log in logs:
                    try:
                        message = json.loads(log['message'])
                        self._process_network_message(message, video_urls)
                    except (json.JSONDecodeError, KeyError):
                        continue
                
                time.sleep(0.5)  # CPU kullanımını azalt
            
            # Duplicate'leri kaldır
            unique_video_urls = list(set(video_urls))
            logger.info(f"Network'den {len(unique_video_urls)} video URL yakalandı")
            
            return unique_video_urls
            
        except Exception as e:
            logger.error(f"Network capture hatası: {e}")
            return []
    
    def _process_network_message(self, message: dict, video_urls: List[str]):
        """Network message'ını işle ve video URL'lerini çıkar"""
        try:
            msg_method = message.get('message', {}).get('method', '')
            
            # Response received events
            if msg_method == 'Network.responseReceived':
                response = message['message']['params']['response']
                url = response.get('url', '')
                mime_type = response.get('mimeType', '')
                
                # Video URL kontrolü
                if self._is_video_url(url, mime_type):
                    video_urls.append(url)
                    logger.debug(f"Video URL yakalandı: {url[:100]}...")
            
            # Request sent events (bazı durumlarda yararlı)
            elif msg_method == 'Network.requestWillBeSent':
                request = message['message']['params']['request']
                url = request.get('url', '')
                
                if self._is_video_url(url):
                    video_urls.append(url)
                    logger.debug(f"Video request yakalandı: {url[:100]}...")
                    
        except Exception as e:
            logger.debug(f"Network message processing error: {e}")
    
    def _is_video_url(self, url: str, mime_type: str = '') -> bool:
        """URL'nin video olup olmadığını kontrol et"""
        if not url or not isinstance(url, str):
            return False
        
        # URL pattern kontrolü
        video_patterns = [
            r'\.mp4',
            r'\.mov',
            r'\.avi',
            r'\.webm',
            r'\.m4v',
            r'/video/',
            r'video\.tiktok',
            r'\.tiktokcdn\.',
            r'\.ttwstatic\.',
            r'\.tiktokv\.',
            r'\.musical\.ly'
        ]
        
        # MIME type kontrolü
        if mime_type:
            if 'video' in mime_type.lower():
                return True
        
        # URL pattern kontrolü
        for pattern in video_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                # Thumbnail/poster image'ları exclude et
                if not re.search(r'(thumb|poster|preview|cover)(?!nail)', url, re.IGNORECASE):
                    return True
        
        return False
    
    def extract_video_from_detail_page(self, ad_element, max_wait: int = 15) -> Optional[str]:
        """Reklam detay sayfasına gidip video URL çıkar"""
        original_window = self.driver.current_window_handle
        
        try:
            # Detay linkini bul
            link_elem = ad_element.find_element(By.CSS_SELECTOR, 'a[href*="detail"]')
            detail_url = link_elem.get_attribute('href')
            
            if not detail_url:
                return None
            
            logger.info(f"Detay sayfasına gidiliyor: {detail_url[:100]}...")
            
            # Yeni tab'da aç
            self.driver.execute_script("window.open(arguments[0], '_blank');", detail_url)
            
            # Yeni tab'a geç
            detail_window = None
            for window in self.driver.window_handles:
                if window != original_window:
                    detail_window = window
                    break
            
            if not detail_window:
                return None
            
            self.driver.switch_to.window(detail_window)
            
            # Network monitoring başlat
            self.start_network_monitoring()
            
            # Sayfa yüklensin ve video player hazır olsun
            time.sleep(3)
            
            # Video element'ini trigger et (play button vs.)
            self._trigger_video_load()
            
            # Network isteklerini yakala
            video_urls = self.capture_network_requests(duration_seconds=max_wait)
            
            # Tab'ı kapat
            self.driver.close()
            self.driver.switch_to.window(original_window)
            
            # En iyi video URL'i seç
            if video_urls:
                best_url = self._select_best_video_url(video_urls)
                logger.info(f"Detay sayfasından video URL bulundu: {best_url[:100]}...")
                return best_url
            
            return None
            
        except Exception as e:
            logger.error(f"Detay sayfası video extraction hatası: {e}")
            
            # Cleanup: Tab'ı kapat
            try:
                if detail_window and detail_window in self.driver.window_handles:
                    self.driver.switch_to.window(detail_window)
                    self.driver.close()
                self.driver.switch_to.window(original_window)
            except:
                pass
            
            return None
    
    def _trigger_video_load(self):
        """Video yüklemeyi tetikle"""
        try:
            # Video elementlerini bul ve play'e bas
            video_triggers = [
                'video',
                '.video-player',
                '.video_player',
                '[data-testid*="video"]',
                '.play-button',
                '[aria-label*="play"]'
            ]
            
            for selector in video_triggers:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        # Click veya hover ile video yüklemeyi tetikle
                        self.driver.execute_script("arguments[0].click();", elem)
                        time.sleep(1)
                        
                        # Video varsa play et
                        if elem.tag_name == 'video':
                            self.driver.execute_script("arguments[0].play();", elem)
                            time.sleep(2)
                            self.driver.execute_script("arguments[0].pause();", elem)
                        
                except Exception:
                    continue
                    
        except Exception as e:
            logger.debug(f"Video trigger hatası: {e}")
    
    def _select_best_video_url(self, video_urls: List[str]) -> str:
        """En iyi video URL'i seç"""
        if not video_urls:
            return None
        
        # Priority order
        priorities = [
            (r'\.mp4', 10),           # MP4 format priority
            (r'\.webm', 8),           # WebM format
            (r'\.mov', 6),            # MOV format
            (r'/video/', 5),          # Video path'li URL'ler
            (r'\.tiktokcdn\.', 8),    # TikTok CDN
            (r'\.ttwstatic\.', 7),    # TikTok static
            (r'high|hd|720|1080', 9), # Yüksek kalite işaretleri
        ]
        
        scored_urls = []
        
        for url in video_urls:
            score = 0
            for pattern, points in priorities:
                if re.search(pattern, url, re.IGNORECASE):
                    score += points
            
            # Daha uzun URL'ler genelde daha detaylı (parameter'lar vs.)
            score += min(len(url) // 100, 3)
            
            scored_urls.append((score, url))
        
        # En yüksek skorlu URL'i döndür
        scored_urls.sort(reverse=True, key=lambda x: x[0])
        
        logger.debug(f"URL skorları: {[(score, url[:50]) for score, url in scored_urls[:3]]}")
        
        return scored_urls[0][1] if scored_urls else video_urls[0]

class TikTokSeleniumScraper:
    """Selenium ile TikTok Ad Library Scraper"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None
        self.base_url = "https://library.tiktok.com"
        self.scraped_ads = []
        
    def setup_driver(self):
        """Chrome WebDriver kurulumu - Modern Selenium ile Network Logging"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument("--headless")
            
            # Temel Chrome argumentları
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Network logging için kritik argumentlar
            chrome_options.add_argument("--enable-logging")
            chrome_options.add_argument("--log-level=0")
            chrome_options.add_argument("--enable-network-service-logging")
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            
            # Modern Selenium için logging preferences
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('prefs', {
                'profile.default_content_setting_values.notifications': 2,
                'profile.default_content_settings.popups': 0,
            })
            
            # Performance logging için modern approach
            chrome_options.set_capability('goog:loggingPrefs', {
                'performance': 'ALL',
                'browser': 'ALL'
            })
            
            # WebDriver oluştur - Modern syntax
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(
                service=service, 
                options=chrome_options
            )
            
            # Chrome DevTools Protocol komutlarını aktifleştir
            self.driver.execute_cdp_cmd('Network.enable', {})
            self.driver.execute_cdp_cmd('Performance.enable', {})
            self.driver.execute_cdp_cmd('Runtime.enable', {})
            
            # Network events'leri dinlemeye başla
            self.driver.execute_cdp_cmd('Network.setCacheDisabled', {'cacheDisabled': True})
            
            logger.info("Chrome WebDriver hazırlandı (Network logging AKTIF)")
            return True
            
        except Exception as e:
            logger.error(f"WebDriver kurulum hatası: {e}")
            return False
    def close_driver(self):
        """WebDriver'ı kapat"""
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver kapatıldı")
    
    def build_search_url(self, 
                        advertiser_name: str = "",
                        region: str = "TR",
                        days_back: int = 30) -> str:
        """TikTok Ad Library arama URL'i oluştur"""
        
        # Tarih aralığı hesapla (Unix timestamp milisaniye)
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days_back)
        
        start_timestamp = int(start_time.timestamp() * 1000)
        end_timestamp = int(end_time.timestamp() * 1000)
        
        url = f"{self.base_url}/ads"
        params = [
            f"region={region}",
            f"start_time={start_timestamp}",
            f"end_time={end_timestamp}",
            f"query_type=1",
            f"sort_type=last_shown_date,desc"
        ]
        
        if advertiser_name:
            params.append(f"adv_name={advertiser_name}")
        
        return url + "?" + "&".join(params)
    
    def search_ads_by_advertiser(self, advertiser_names: List[str], max_ads: int = 100) -> List[Dict]:
        """Reklam veren adlarına göre reklam ara"""
        all_ads = []
        
        if not self.setup_driver():
            logger.error("WebDriver kurulamadı")
            return []
        
        try:
            for advertiser in advertiser_names:
                logger.info(f"'{advertiser}' reklamları aranıyor...")
                
                search_url = self.build_search_url(advertiser_name=advertiser)
                logger.info(f"URL: {search_url}")
                
                ads = self._scrape_ads_from_url(search_url, max_ads_per_search=20)
                all_ads.extend(ads)
                
                logger.info(f"'{advertiser}' için {len(ads)} reklam bulundu")
                
                # Rate limiting
                safe_sleep(3, 5)
                
                if len(all_ads) >= max_ads:
                    break
            
            logger.info(f"Toplam {len(all_ads)} reklam scrape edildi")
            
        except Exception as e:
            logger.error(f"Selenium scraping hatası: {e}")
        
        finally:
            self.close_driver()
        
        return all_ads
    
    def search_banking_ads(self, max_ads: int = 100) -> List[Dict]:
        """Türk bankalarının reklamlarını ara"""
        
        # Türk bankaları listesi
        turkish_banks = [
            "garanti", "isbank", "yapikredi", "akbank", "halkbank", "vakifbank",
            "denizbank", "ingbank", "teb", "finansbank", "kuveytturk", "albaraka",
            "papara", "ininal", "tosla", "param", "ziraat", "enpara"
        ]
        
        return self.search_ads_by_advertiser(turkish_banks, max_ads)
    
    def _scrape_ads_from_url(self, url: str, max_ads_per_search: int = 20) -> List[Dict]:
        """Belirli URL'den reklamları scrape et"""
        ads = []
        
        try:
            self.driver.get(url)
            
            # Sayfanın yüklenmesini bekle
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Biraz bekle, dinamik içerik için
            time.sleep(5)
            
            # Reklam kartlarını bul
            ad_elements = self._find_ad_elements()
            
            if not ad_elements:
                logger.warning("Reklam bulunamadı, sayfa yapısı değişmiş olabilir")
                return []
            
            logger.info(f"{len(ad_elements)} reklam elementi bulundu")
            
            # Her reklam için detay çıkar
            for i, ad_element in enumerate(ad_elements[:max_ads_per_search]):
                try:
                    ad_data = self._extract_ad_data(ad_element, i)
                    if ad_data:
                        ads.append(ad_data)
                        
                except Exception as e:
                    logger.warning(f"Reklam {i+1} işlenirken hata: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"URL scraping hatası: {e}")
        
        return ads
    
    def _find_ad_elements(self) -> List:
        """Sayfadaki reklam elementlerini bul - TikTok gerçek yapısı"""
        try:
            # TikTok'un gerçek CSS selector'ı
            main_selector = '.ad_card'
            
            # Ana reklam kartlarını bul
            elements = self.driver.find_elements(By.CSS_SELECTOR, main_selector)
            
            if elements:
                logger.info(f"TikTok reklam kartları bulundu: {len(elements)} adet (.ad_card)")
                return elements
            else:
                logger.warning("Hiçbir .ad_card elementi bulunamadı")
                return []
            
        except Exception as e:
            logger.error(f"Element bulma hatası: {e}")
            return []
    
    def _extract_ad_data(self, ad_element, index: int) -> Optional[Dict]:
        """Reklam elementinden veri çıkar"""
        try:
            ad_data = {
                'scrape_index': index,
                'scraped_at': datetime.now().isoformat(),
                'advertiser_name': 'Unknown',
                'ad_text': '',
                'media_urls': [],
                'ad_url': '',
                'first_shown': '',
                'last_shown': '',
                'reach': ''
            }
            
            # Selenium element ise
            if hasattr(ad_element, 'find_element'):
                ad_data.update(self._extract_from_selenium_element(ad_element))
            else:
                # BeautifulSoup element ise
                ad_data.update(self._extract_from_bs_element(ad_element))
            
            # Temel doğrulama
            if not ad_data.get('advertiser_name') or ad_data['advertiser_name'] == 'Unknown':
                logger.warning(f"Reklam {index}: Advertiser name bulunamadı")
            
            return ad_data
            
        except Exception as e:
            logger.warning(f"Reklam {index} veri çıkarma hatası: {e}")
            return None
    
    def _extract_from_selenium_element(self, element) -> Dict:
        """Enhanced video extraction with network monitoring"""
        data = {}
        
        try:
            # NetworkVideoExtractor kullan
            video_extractor = NetworkVideoExtractor(self.driver)
            
            # Detay sayfasından gerçek video URL'i al
            video_url = video_extractor.extract_video_from_detail_page(element)
            
            if video_url:
                data['media_urls'] = [video_url]
                data['media_type'] = 'video'
                data['video_found'] = True
                data['extraction_method'] = 'network_detail_page'
                logger.info(f"✅ Network'den video URL bulundu")
            else:
                # Fallback: Original thumbnail method
                data.update(self._original_media_extraction(element))
                data['video_found'] = False
                data['extraction_method'] = 'fallback_thumbnail'
            
            # Diğer ad bilgilerini çıkar
            data.update(self._extract_ad_metadata(element))
            
        except Exception as e:
            logger.error(f"Enhanced extraction hatası: {e}")
            data.update(self._original_media_extraction(element))
            data.update(self._extract_ad_metadata(element))
        
        return data

    def _trigger_main_page_video_load(self, element):
        """Ana sayfadaki video yüklemeyi tetikle"""
        try:
            # Video player'a hover et
            video_player = element.find_element(By.CSS_SELECTOR, '.video_player')
            self.driver.execute_script("""
                arguments[0].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
                arguments[0].dispatchEvent(new MouseEvent('mouseenter', {bubbles: true}));
            """, video_player)
            
            time.sleep(1)
            
            # Click et
            self.driver.execute_script("arguments[0].click();", video_player)
            
            time.sleep(2)
            
        except Exception as e:
            logger.debug(f"Video trigger hatası: {e}")

    def _extract_ad_metadata(self, element) -> Dict:
        """Reklam meta verilerini çıkar"""
        data = {}
        
        try:
            # Advertiser name
            try:
                advertiser_elem = element.find_element(By.CSS_SELECTOR, '.ad_info_text')
                advertiser_text = clean_text(advertiser_elem.text)
                if advertiser_text and len(advertiser_text) > 2:
                    data['advertiser_name'] = advertiser_text
            except:
                data['advertiser_name'] = 'Unknown'
            
            # Ad details
            try:
                detail_elem = element.find_element(By.CSS_SELECTOR, '.ad_detail')
                detail_text = detail_elem.text
                
                lines = detail_text.split('\n')
                for line in lines:
                    line = line.strip()
                    if 'First shown:' in line:
                        data['first_shown'] = line.replace('First shown:', '').strip()
                    elif 'Last shown:' in line:
                        data['last_shown'] = line.replace('Last shown:', '').strip()
                    elif 'Unique users seen:' in line:
                        data['reach'] = line.replace('Unique users seen:', '').strip()
            except:
                pass
            
            # Ad ID ve detail URL
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, 'a')
                href = link_elem.get_attribute('href')
                if href and 'ad_id=' in href:
                    ad_id = href.split('ad_id=')[1].split('&')[0]
                    data['ad_id'] = ad_id
                    data['detail_url'] = href
            except:
                pass
            
            # Ad text
            try:
                full_text = clean_text(element.text)
                if len(full_text) > 20:
                    data['ad_text'] = full_text[:500] + ('...' if len(full_text) > 500 else '')
            except:
                data['ad_text'] = ''
        
        except Exception as e:
            logger.debug(f"Metadata extraction hatası: {e}")
        
        return data

    def _original_media_extraction(self, element) -> Dict:
        """Original extraction method (fallback)"""
        data = {
            'media_urls': [],
            'media_type': 'text',
            'video_found': False,
            'extraction_method': 'fallback_original'
        }
        
        try:
            # Background image extraction
            video_player = element.find_element(By.CSS_SELECTOR, '.video_player')
            style = video_player.get_attribute('style')
            if style and 'background-image: url(' in style:
                url_match = re.search(r'background-image:\s*url\(["\']?(.*?)["\']?\)', style)
                if url_match:
                    media_url = url_match.group(1)
                    data['media_urls'] = [media_url]
                    data['media_type'] = 'image'  # Bu genellikle thumbnail
                    logger.warning(f"⚠️ Sadece thumbnail URL bulundu: {media_url[:100]}...")
        except:
            pass
        
        return data
    
    def _extract_from_bs_element(self, element) -> Dict:
        """BeautifulSoup elementinden veri çıkar"""
        data = {}
        
        try:
            # Text içeriğini al
            text_content = element.get_text(strip=True)
            if len(text_content) > 20:  # Anlamlı içerik varsa
                data['ad_text'] = clean_text(text_content[:200])
            
            # Images
            images = element.find_all('img')
            data['media_urls'] = [img.get('src') for img in images if img.get('src')]
            
            # Links
            links = element.find_all('a', href=True)
            if links:
                data['ad_url'] = links[0]['href']
                
        except Exception as e:
            logger.debug(f"BeautifulSoup extraction error: {e}")
        
        return data
    
    def save_screenshot(self, filename: str = None):
        """Debug için screenshot al"""
        if not self.driver:
            return
            
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/debug/screenshot_{timestamp}.png"
        
        try:
            import os
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            self.driver.save_screenshot(filename)
            logger.info(f"Screenshot kaydedildi: {filename}")
        except Exception as e:
            logger.error(f"Screenshot kaydetme hatası: {e}")