## Konfigürasyon (.env ve ortam değişkenleri)

Bu proje ayarlarını `src/config/settings.py` içinden alır. Bu dosya:

- `.env` dosyasını okur (`load_dotenv()` + `pydantic-settings`)
- Bulamazsa varsayılan değerlerle devam eder

### `.env` nasıl oluşturulur?

Proje kök dizinine (README’nin olduğu yere) `.env` adlı bir dosya koyabilirsiniz.

Örnek `.env`:

```env
# Genel
LOG_LEVEL=INFO

# Bankacılık anahtar kelimeleri (virgülle ayır)
BANKING_KEYWORDS=banka,kredi,kart,finans,faiz,kampanya

# FastAPI port (opsiyonel)
PORT=8000
```

---

## Ortam değişkenleri (tam liste)

`Settings` sınıfındaki alanlar:

### TikTok

- `TIKTOK_BASE_URL` (varsayılan: `https://library.tiktok.com`)
- `TIKTOK_API_VERSION` (varsayılan: `v1`)
- `TIKTOK_COUNTRY` (varsayılan: `TR`)
- `TIKTOK_SESSION_TIMEOUT` (varsayılan: `300`)
- `TIKTOK_MAX_ADS_PER_SEARCH` (varsayılan: `200`)

### Proxy (şu an kodda aktif kullanılmıyor)

- `USE_PROXIES` (varsayılan: `false`)
- `PROXY_ROTATION_INTERVAL` (varsayılan: `10`)
- `MAX_RETRIES` (varsayılan: `3`)

### Rate limiting

- `REQUESTS_PER_MINUTE` (varsayılan: `30`)
- `DELAY_BETWEEN_REQUESTS` (varsayılan: `2`)

### Database (şu an aktif kullanılmıyor)

- `DB_TYPE` (varsayılan: `sqlite`)
- `DB_URL` (varsayılan: `sqlite:///data\\ads.db`)

### Logging

- `LOG_LEVEL` (varsayılan: `INFO`)
- `LOG_FILE` (varsayılan: `logs\\scraper.log`)

### Banking keywords

- `BANKING_KEYWORDS`
  - virgülle ayrılmış string beklenir
  - ör: `BANKING_KEYWORDS=banka,kredi,kart`

### Dosya yolları

Not: Varsayılanlar Windows path (`\\`) kullanıyor. Linux’ta da çalışır, ama isterseniz `/` kullanarak override edebilirsiniz.

- `MEDIA_DOWNLOAD_PATH` (varsayılan: `data\\media`)
- `RAW_DATA_PATH` (varsayılan: `data\\raw`)
- `PROCESSED_DATA_PATH` (varsayılan: `data\\processed`)

### User-Agent

- `ROTATE_USER_AGENTS` (varsayılan: `true`)

