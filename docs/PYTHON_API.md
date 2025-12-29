## Python Public API dokümantasyonu

Bu dosya, `src/` altındaki public sınıf/fonksiyonları “yeni başlayan” seviyesinde anlatır.

> Not: “Public” derken; başka dosyalardan import edilip kullanılabilen, class/fonksiyon olarak yazılmış parçaları kastediyoruz. Başında `_` olanlar genelde “private/helper” kabul edilir.

---

## `src/config/settings.py`

### `Settings`

Projenin ayarlarını tutan sınıftır. `pydantic-settings` ile çalışır ve `.env` dosyasını otomatik okur.

- **Ne işe yarar?**
  - TikTok/ülke ayarları
  - Rate limit ayarları
  - Dosya yolları
  - Log ayarları
  - Bankacılık anahtar kelimeleri

### `settings`

`Settings()` sınıfından oluşturulmuş **global** nesnedir. Kodun her yerinde şöyle kullanılır:

```python
from src.config.settings import settings

print(settings.tiktok_country)
```

---

## `src/models/ad_model.py`

Bu dosya “çıktı verisini” standartlaştırır. Scraper çalışınca **TikTokAd** listesi üretir ve özet için **ScrapingResult** döndürür.

### `MediaType` (Enum)

- `MediaType.VIDEO` → `"video"`
- `MediaType.IMAGE` → `"image"`
- `MediaType.TEXT` → `"text"`

### `TikTokAd` (Pydantic model)

Bir reklamı temsil eder.

En sık kullanılan alanlar:

- `ad_id` (str)
- `advertiser_name` (str)
- `ad_text` (str | None)
- `media_type` (`MediaType`)
- `media_urls` (list[str])
- `is_banking_ad` (bool)
- `banking_keywords_found` (list[str])
- `scraped_at` (datetime)
- `source_url` (str | None)
- `raw_data` (dict)

Kullanışlı metotlar:

- `is_video()` → video mu?
- `is_image()` → resim mi?

### `ScrapingResult` (Pydantic model)

Scraper’ın “kaç tane bulundu, kaç tanesi video, ne kadar sürdü” gibi özet bilgisidir.

Önemli alanlar:

- `total_ads`, `banking_ads`, `video_ads`, `image_ads`, `text_ads`, `failed_ads`
- `duration_seconds`
- `errors` (list[str])

Önemli metotlar:

- `complete()` → bitiş zamanını set eder ve `duration_seconds` hesaplar.
- `add_error(error)` → hatayı `errors` içine ekler.

---

## `src/utils/helpers.py`

### `is_banking_related(text, keywords) -> (bool, list[str])`

Verilen metin içinde, verilen anahtar kelimeler geçiyor mu kontrol eder.

```python
from src.utils.helpers import is_banking_related

is_banking, found = is_banking_related(
    "Garanti ile kredi başvurusu",
    ["banka", "kredi", "kart"]
)
```

### `clean_text(text) -> str`

HTML tag’larını ve fazla boşlukları temizler.

### `extract_urls_from_text(text) -> list[str]`

Metin içinden `http/https` linklerini regex ile çıkarır.

### `safe_sleep(min_seconds=1.0, max_seconds=3.0)`

Random gecikme yapar (rate limit / bot gibi görünmemek için).

### `format_datetime(dt) -> str` / `parse_datetime(dt_str) -> datetime | None`

Datetime formatlama / parse etme yardımcıları.

### `create_filename_safe(text, max_length=50) -> str`

Dosya adı için güvenli string üretir (Türkçe karakterleri sadeleştirir, boşlukları `_` yapar).

> Not: Bu dosya import edildiğinde `logger.info("Helper functions loaded")` log’u atar. Yani sadece import bile log üretir.

---

## `src/scraper/tiktok_scraper.py`

### `TikTokAdScraper`

Bu, “yüksek seviye” scraper sınıfıdır. İçeride Selenium tabanlı scraper’ı (`TikTokSeleniumScraper`) kullanır.

#### `__init__(headless=True)`

- `headless=True` → arkaplanda Chrome çalışır (sunucular için ideal)
- `headless=False` → Chrome penceresini görürsünüz (debug için ideal)

#### `search_ads(keywords, max_results=200) -> ScrapingResult`

TikTok reklamlarını toplar.

Önemli not: Bu sürümde `keywords` parametresi doğrudan TikTok aramasına uygulanmıyor; içeride `search_banking_ads()` çağrısı ile Türk banka listesine göre çekim yapılıyor. (Yani şu an daha çok “bankalara göre” çalışıyor.)

Örnek:

```python
from src.scraper.tiktok_scraper import TikTokAdScraper

scraper = TikTokAdScraper(headless=True)
result = scraper.search_ads(keywords=["banka", "kredi"], max_results=50)

print(result.total_ads, result.banking_ads)
print(len(scraper.scraped_ads))
```

#### `save_results(filepath=None) -> str`

Toplanan reklamları JSON olarak diske yazar ve dosya yolunu döndürür.

#### `get_banking_ads() -> list[TikTokAd]`

Sadece `is_banking_ad=True` olanları döndürür.

#### `get_video_ads() -> list[TikTokAd]`

Sadece video olanları döndürür.

---

## `src/scraper/tiktok_selenium_scraper.py`

### `TikTokSeleniumScraper`

TikTok Ad Library sayfasını Selenium ile açar ve reklam kartlarından bilgi çıkarmaya çalışır.

En önemli public metotlar:

- `setup_driver()` → Chrome’u hazırlar (CDP + performance log açık)
- `close_driver()` → Chrome’u kapatır
- `build_search_url(advertiser_name="", region="TR", days_back=30) -> str` → arama URL’i üretir
- `search_ads_by_advertiser(advertiser_names, max_ads=100) -> list[dict]`
- `search_banking_ads(max_ads=100) -> list[dict]` → gömülü Türk bankaları listesiyle arar
- `save_screenshot(filename=None)` → debug için ekran görüntüsü alır

### `NetworkVideoExtractor`

Amaç: Reklam kartındaki **gerçek video URL**’ini “network logs” üzerinden yakalamak.

Önemli metotlar:

- `start_network_monitoring()`
- `capture_network_requests(duration_seconds=10) -> list[str]`
- `extract_video_from_detail_page(ad_element, max_wait=15) -> str | None`

---

## Kök dizindeki yardımcı script’ler

Bu script’ler daha çok “manuel debug / test” içindir:

- `main.py`: terminalden basit çalışma örneği (scrape + özet + kaydet)
- `n8n_tiktok_scraper.py`: N8N için CLI wrapper (stdout’a JSON basar)
- `debug_scraper.py`, `quick_test.py`, `quick_debug.py`, `debug_media.py`, `test_network_video.py`: Selenium selector / video extraction debug’ları

