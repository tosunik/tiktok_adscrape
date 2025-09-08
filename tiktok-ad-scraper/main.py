import sys
import os
from pathlib import Path
from loguru import logger
from datetime import datetime

# Proje modüllerini import et
from src.config.settings import settings
from src.scraper.tiktok_scraper import TikTokAdScraper
from src.utils.helpers import format_datetime

def setup_logging():
    """Logging yapılandırması"""
    # Log klasörünü oluştur
    Path("logs").mkdir(exist_ok=True)
    
    # Loguru konfigürasyonu
    logger.remove()  # Varsayılan handler'ı kaldır
    
    # Konsol logging
    logger.add(
        sys.stdout,
        level=settings.log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Dosya logging
    logger.add(
        settings.log_file,
        level=settings.log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
        encoding="utf-8"
    )

def main():
    """Ana uygulama fonksiyonu"""
    setup_logging()
    logger.info("🚀 TikTok Ad Scraper başlatılıyor...")
    
    try:
        # Scraper'ı oluştur
        scraper = TikTokAdScraper()
        logger.info("Scraper oluşturuldu")
        
        # Bankacılık anahtar kelimeleri ile ara
        banking_keywords = ["banka", "kredi", "kart", "finans"]
        logger.info(f"Arama anahtar kelimeleri: {banking_keywords}")
        
        # Scraping'i başlat
        result = scraper.search_ads(
            keywords=banking_keywords,
            max_results=settings.tiktok_max_ads_per_search
        )
        
        # Sonuçları göster
        print("\n" + "="*50)
        print("📊 SCRAPING SONUÇLARI")
        print("="*50)
        print(f"🎯 Toplam Reklam: {result.total_ads}")
        print(f"🏦 Banking Reklamları: {result.banking_ads}")
        print(f"🎬 Video Reklamları: {result.video_ads}")
        print(f"🖼️  Resim Reklamları: {result.image_ads}")
        print(f"📝 Metin Reklamları: {result.text_ads}")
        print(f"❌ Başarısız: {result.failed_ads}")
        
        # Duration hesapla
        duration = result.duration_seconds if result.duration_seconds is not None else 0
        print(f"⏱️  Süre: {duration:.2f} saniye")
        print("="*50)
        
        # Hatalar varsa göster
        if result.errors:
            print("\n⚠️  HATALAR:")
            for error in result.errors:
                print(f"  • {error}")
        
        # Banking reklamlarını göster
        banking_ads = scraper.get_banking_ads()
        if banking_ads:
            print(f"\n🏦 BANKING REKLAMLARI ({len(banking_ads)} adet):")
            print("-" * 40)
            
            for i, ad in enumerate(banking_ads[:5], 1):  # İlk 5'ini göster
                print(f"\n{i}. {ad.advertiser_name}")
                print(f"   📝 Metin: {ad.ad_text[:100]}...")
                print(f"   🎯 Medya: {ad.media_type.value}")
                print(f"   🔍 Anahtar Kelimeler: {', '.join(ad.banking_keywords_found)}")
                print(f"   📅 Tarih: {format_datetime(ad.scraped_at)}")
        
        # Sonuçları kaydet
        if result.total_ads > 0:
            saved_file = scraper.save_results()
            print(f"\n💾 Sonuçlar kaydedildi: {saved_file}")
        
        logger.info("✅ Scraping başarıyla tamamlandı!")
        
    except KeyboardInterrupt:
        logger.info("❌ Kullanıcı tarafından durduruldu")
        print("\n🛑 İşlem durduruldu")
        
    except Exception as e:
        logger.error(f"❌ Beklenmeyen hata: {e}")
        print(f"\n❌ Hata: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)