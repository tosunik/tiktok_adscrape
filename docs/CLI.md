## Komut satırı (CLI) kullanım rehberi

Bu repo’da “doğrudan çalıştırılabilen” 3 ana giriş noktası var:

- `main.py` (basit demo/çalıştırma)
- `fastapi_server.py` (HTTP API)
- `n8n_tiktok_scraper.py` (N8N için CLI wrapper)

---

## 1) `main.py` (en basit kullanım)

### Ne yapar?

- Logging’i ayarlar
- `TikTokAdScraper()` ile scraping yapar
- Sonucu ekrana özet olarak basar
- Reklam bulduysa JSON dosyası olarak kaydeder

### Çalıştırma

```bash
python main.py
```

> Not: `main.py` içinde örnek keyword listesi hard-code: `["banka", "kredi", "kart", "finans"]`

---

## 2) `fastapi_server.py` (N8N için HTTP API)

FastAPI sunucu kullanımını `docs/API.md` içinde detaylı anlattım.

Kısa başlatma:

```bash
python fastapi_server.py
```

---

## 3) `n8n_tiktok_scraper.py` (stdout’a JSON basar)

Bu script, N8N’de “Execute Command” gibi adımlarla çalıştırmaya uygundur.

### Temel kullanım

```bash
python n8n_tiktok_scraper.py --keywords "banka,kredi" --max-results 50
```

### Parametreler

- `--keywords`: virgülle ayrılmış kelimeler (default: `banka,kredi,kart,finans`)
- `--max-results`: maksimum reklam sayısı (default: `100`)
- `--output-format`: `n8n` veya `json` (default: `n8n`)

### `--output-format n8n` ne üretir?

- Çıktı: **array of objects**
- Her ad objesinin içinde `n8n_meta` alanı olur (küçük özet bilgiler)

### `--output-format json` ne üretir?

- Çıktı: `{ summary: {...}, ads: [...] }` şeklinde tek JSON obje

