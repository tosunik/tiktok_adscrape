# TikTok Ad Scraper

Bu proje, TikTok platformunda bankacılık ve finans sektörüne ait reklamları otomatik olarak toplayan bir Python uygulamasıdır. N8N workflow'ları ile entegre çalışabilir.

Bu satır GitHub push testi içindir. Herhangi bir işlevi değiştirmez.

## 🚀 Özellikler

- **TikTok Reklam Toplama**: Belirtilen anahtar kelimelerle TikTok reklamlarını otomatik toplar
- **Bankacılık Filtreleme**: Bankacılık ve finans sektörüne özel anahtar kelime filtreleme
- **Medya Türü Desteği**: Video, resim ve metin reklamlarını destekler
- **N8N Entegrasyonu**: FastAPI ile N8N workflow'larına entegre edilebilir
- **Veri Kaydetme**: JSON formatında sonuçları kaydeder
- **Logging**: Detaylı log kayıtları tutar

## 📋 Gereksinimler

- Python 3.8+
- Chrome/Chromium tarayıcı
- İnternet bağlantısı

## 🛠️ Kurulum

1. **Repository'yi klonlayın:**
```bash
git clone https://github.com/tosunik/tiktok_adscrape.git
cd tiktok_adscrape
```

2. **Sanal ortam oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# veya
venv\Scripts\activate     # Windows
```

3. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

## 🎯 Kullanım

### Temel Kullanım

```bash
python main.py
```

### FastAPI Server (N8N için)

```bash
python fastapi_server.py
```

Server `http://localhost:8000` adresinde çalışacaktır.

### API Endpoints

- `GET /health` - Sağlık kontrolü
- `POST /scrape` - Reklam toplama işlemi başlatır
- `GET /results` - Sonuçları getirir

## 📁 Proje Yapısı

```
tiktok-ad-scraper/
├── src/
│   ├── config/          # Yapılandırma dosyaları
│   ├── models/          # Veri modelleri
│   ├── scraper/         # Scraping mantığı
│   └── utils/           # Yardımcı fonksiyonlar
├── data/               # Toplanan veriler
├── logs/               # Log dosyaları
├── main.py             # Ana uygulama
├── fastapi_server.py   # N8N entegrasyonu
└── requirements.txt    # Python bağımlılıkları
```

## ⚙️ Yapılandırma

Uygulama ayarları `src/config/settings.py` dosyasında bulunur:

- `tiktok_max_ads_per_search`: Arama başına maksimum reklam sayısı
- `log_level`: Log seviyesi
- `log_file`: Log dosya yolu

## 📊 Çıktı Formatı

Toplanan reklamlar JSON formatında `data/raw/` klasörüne kaydedilir:

```json
{
  "total_ads": 50,
  "banking_ads": 12,
  "video_ads": 30,
  "image_ads": 15,
  "text_ads": 5,
  "failed_ads": 3,
  "duration_seconds": 45.2,
  "scraped_at": "2024-01-01T12:00:00Z"
}
```

## 🔧 Geliştirme

### Test Çalıştırma

```bash
python -m pytest
```

### Kod Formatlama

```bash
black .
flake8 .
```

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## ⚠️ Uyarılar

- Bu araç sadece eğitim ve araştırma amaçlıdır
- TikTok'un kullanım şartlarına uygun şekilde kullanın
- Rate limiting ve etik scraping kurallarına uyun
- Kişisel verileri koruma yasalarına dikkat edin

## 📞 İletişim

Sorularınız için issue açabilir veya iletişime geçebilirsiniz.
