# 📰 Dünün Teknoloji Haberleri

Her gün Türkiye saati 08:00'da otomatik güncellenen teknoloji haber sitesi.

## 🚀 Kurulum (5 dakika)

### Adım 1: Bu repo'yu oluşturun
1. GitHub'da yeni repo oluşturun: `dununhaberleri`
2. **Public** olarak ayarlayın

### Adım 2: Dosyaları yükleyin
Repo'nuza şu dosyaları yükleyin:
```
├── index.html              ← Ana site dosyası
├── update_news.py          ← Haber güncelleme scripti
├── .github/
│   └── workflows/
│       └── daily-update.yml  ← Günlük otomasyon
└── README.md               ← Bu dosya
```

### Adım 3: Anthropic API Key ekleyin
1. [console.anthropic.com](https://console.anthropic.com/) → API Keys → Create Key
2. GitHub repo → **Settings** → **Secrets and variables** → **Actions**
3. **New repository secret** tıklayın
4. Name: `ANTHROPIC_API_KEY`
5. Secret: API anahtarınızı yapıştırın
6. **Add secret** tıklayın

### Adım 4: GitHub Pages'i aktifleştirin
1. Repo → **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `/ (root)`
4. **Save**

### Adım 5: Bitti! 🎉
- Site: `https://KULLANICIADI.github.io/dununhaberleri/`
- Her gün 08:00 TR saatinde otomatik güncellenir

---

## ⚙️ Nasıl Çalışır?

```
Her gün 08:00 (TR) → GitHub Actions tetiklenir
         ↓
  update_news.py çalışır
         ↓
  Claude API ile dünkü haberler toplanır
  (web search ile gerçek kaynaklardan)
         ↓
  index.html güncellenir
  (yeni haberler eklenir, arşiv korunur)
         ↓
  Otomatik commit & push
         ↓
  GitHub Pages anında güncellenir
         ↓
  Site canlı! 🎉
```

## 🔧 Manuel Tetikleme

Otomatik güncellemeyi beklemeden çalıştırmak için:
1. Repo → **Actions** sekmesi
2. Sol menüden **"Günlük Haber Güncelleme"** seçin
3. **"Run workflow"** → **"Run workflow"** tıklayın

## 💰 Maliyet

| Hizmet | Maliyet |
|--------|---------|
| GitHub Pages | Ücretsiz |
| GitHub Actions | Ücretsiz (2000 dk/ay) |
| Anthropic API | ~$0.05-0.10/gün (~$2-3/ay) |

> Script günde 1 kez çalışır ve yaklaşık 1 API çağrısı yapar.
> Claude Sonnet kullanılır (düşük maliyet, yüksek kalite).

## 📋 Özel Domain (Opsiyonel)

1. Domain satın alın (ör. Namecheap, GoDaddy)
2. DNS'te CNAME kaydı ekleyin: `KULLANICIADI.github.io`
3. GitHub → Settings → Pages → Custom domain → domain adresinizi yazın
4. "Enforce HTTPS" kutusunu işaretleyin

## 🗂️ Arşiv

- Son 90 günlük haberler otomatik olarak saklanır
- Takvimden geçmiş günlere tıklayarak arşive erişilebilir
- 90 günden eski haberler otomatik temizlenir

## 🟩 Tekno Wordle

- Her gün yeni bir 5 harfli Türkçe teknoloji kelimesi
- Türkçe klavye desteği (Ğ, Ü, Ş, İ, Ö, Ç)
- İlerleme localStorage'da saklanır
- Gece yarısı otomatik yenilenir

---

**LinkedIn:** [Dünün Teknoloji Haberleri](https://www.linkedin.com/company/d%C3%BCn%C3%BCn-teknoloji-haberi/)
