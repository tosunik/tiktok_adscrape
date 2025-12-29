## FastAPI (N8N entegrasyonu) dokümantasyonu

Bu dosya `fastapi_server.py` içindeki **HTTP API**’yi açıklar.

### Sunucuyu çalıştırma

1) Bağımlılıkları kur:

```bash
pip install -r requirements.txt
```

2) Sunucuyu başlat:

```bash
python fastapi_server.py
```

3) Varsayılan adres:

- `http://localhost:8000`

Not: Port’u değiştirmek için `PORT` ortam değişkeni kullanılabilir:

```bash
PORT=9000 python fastapi_server.py
```

### Ortak notlar

- **CORS**: Her yerden istek kabul edecek şekilde açıktır (`allow_origins=["*"]`). N8N gibi dış servislerden rahatça çağırılabilsin diye.
- **Yanıt formatı**: Bazı uçlar **liste** döndürür (özellikle N8N’nin sevdiği “array of objects” formatı).

---

## Endpoint: `GET /`

### Amaç
API’nin ayakta olduğunu ve hangi uçların olduğunu hızlıca görmek.

### Örnek istek

```bash
curl -s http://localhost:8000/ | python -m json.tool
```

### Örnek yanıt

```json
{
  "message": "TikTok Banking Ad Intelligence API",
  "status": "running",
  "endpoints": ["/health", "/scrape-tiktok", "/test-scrape", "/turkish-banks"]
}
```

---

## Endpoint: `GET /health`

### Amaç
N8N monitoring / uptime kontrolü.

### Örnek istek

```bash
curl -s http://localhost:8000/health | python -m json.tool
```

### Örnek başarılı yanıt

```json
{
  "status": "healthy",
  "service": "TikTok Banking Ad Scraper",
  "version": "1.0.0",
  "settings_loaded": true,
  "banking_keywords_count": 0
}
```

Not: `banking_keywords_count`, `settings.banking_keywords` listesinin uzunluğudur. `.env` ile `BANKING_KEYWORDS` verilmezse `0` kalabilir.

---

## Endpoint: `GET /test-selenium`

### Amaç
Bu makinede Selenium + Chrome/Chromium çalışıyor mu hızlı test etmek.

### Örnek istek

```bash
curl -s http://localhost:8000/test-selenium | python -m json.tool
```

### Örnek yanıtlar

Başarılı:

```json
{
  "selenium_works": true,
  "chrome_installed": true
}
```

Başarısız:

```json
{
  "selenium_works": false,
  "error": "....",
  "chrome_installed": false
}
```

---

## Endpoint: `GET /turkish-banks`

### Amaç
N8N UI’da dropdown gibi yerlerde kullanılabilsin diye Türk banka/fintek listesini döndürmek.

### Örnek istek

```bash
curl -s http://localhost:8000/turkish-banks | python -m json.tool
```

### Yanıt alanları

- `all_banks`: `src/config/settings.py` içindeki `settings.turkish_banks`
- `major_banks`: sabit “büyük bankalar” listesi
- `digital_fintech`: sabit “dijital/fintek” listesi

---

## Endpoint: `GET /test-scrape`

### Amaç
Sistemin uçtan uca çalışıp çalışmadığını görmek için küçük bir deneme scrape’i.

### Ne yapar?
- `TikTokAdScraper(headless=True)` başlatır
- `keywords=["garanti"]` ile `max_results=3` şekilde arar
- Özet + ilk reklamın örneğini döndürür

### Örnek istek

```bash
curl -s http://localhost:8000/test-scrape | python -m json.tool
```

---

## Endpoint: `POST /scrape-tiktok`

### Amaç
Asıl scraping endpoint’i. N8N akışından çağırıp, çıkan reklamları işlemek için kullanılır.

### İstek gövdesi (JSON)

`ScrapeRequest` modeli:

- `keywords` (list[str]): aranacak kelimeler (varsayılan: `["banka","kredi","garanti","akbank"]`)
- `max_results` (int): 1–200 arası (varsayılan: 50)
- `region` (str): varsayılan `"TR"` (şu an scraping tarafında URL üretiminde kullanılmıyor)
- `days_back` (int): 1–30 arası (şu an scraping tarafında kullanılmıyor)
- `banking_only` (bool): sadece bankacılık reklamlarını döndür (varsayılan: true)
- `headless` (bool): Chrome headless çalışsın mı (varsayılan: true)

### Örnek istek

```bash
curl -s -X POST "http://localhost:8000/scrape-tiktok" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["garanti", "kredi"],
    "max_results": 20,
    "banking_only": true,
    "headless": true
  }' | python -m json.tool
```

### Yanıt (N8N uyumlu)

Yanıt **doğrudan bir liste** döndürür: `[{...ad...}, {...ad...}]`

Her item içinde temel alanlar:

- `ad_id`
- `advertiser_name`
- `ad_text`
- `media_type` (`"video" | "image" | "text"`)
- `media_urls` (list[str])
- `is_banking_ad` (bool)
- `banking_keywords_found` (list[str])
- `scraped_at` (ISO string)
- `first_shown`, `last_shown`, `source_url` (varsa)
- `n8n_meta` (N8N işlemleri için ek özet alanlar)
- `scrape_summary` (her item’e eklenen genel özet)

### Hata yanıtı

- HTTP 500 döner
- `detail` içinde `error`, `type`, `success` alanları olur

