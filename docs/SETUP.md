## Lokal kurulum (Linux için)

### 1) Python bağımlılıkları

Proje kök dizininde:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Chrome/Chromium gereksinimi

Scraper Selenium kullandığı için sistemde **Chrome/Chromium** gerekir.

- Birçok Linux ortamında `google-chrome` veya `chromium` paketleriyle kurulur.
- Repo, `webdriver-manager` kullandığı için genelde driver’ı otomatik indirir.

### 3) Hızlı deneme

FastAPI ile:

```bash
python fastapi_server.py
curl -s http://localhost:8000/health
```

CLI ile:

```bash
python n8n_tiktok_scraper.py --keywords "garanti,kredi" --max-results 5
```

### 4) Sık karşılaşılan problemler

#### Chrome açılmıyor / “no such file or directory”

- Chrome/Chromium sistemde kurulu olmayabilir.
- Bazı container ortamlarında `--no-sandbox` gerekir (kod zaten ekliyor).

#### Headless çalışıyor ama “ekranda görmek istiyorum”

- `TikTokAdScraper(headless=False)` veya `TikTokSeleniumScraper(headless=False)` kullanın.
- Debug script’leri: `debug_scraper.py`, `quick_test.py`, `debug_media.py`

