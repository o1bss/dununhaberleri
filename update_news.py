#!/usr/bin/env python3
"""
Dünün Teknoloji Haberleri - Günlük Otomatik Güncelleme Scripti
Her gün Türkiye saati 08:00'da GitHub Actions tarafından çalıştırılır.
Claude API kullanarak dünkü haberleri toplar ve index.html'i günceller.
"""

import os
import json
import re
from datetime import datetime, timedelta, timezone

import anthropic


# ─── AYARLAR ───
TURKEY_TZ = timezone(timedelta(hours=3))
SITE_FILE = "index.html"
MAX_ARCHIVE_DAYS = 90  # Kaç günlük arşiv tutulsun


def get_yesterday_date():
    """Türkiye saatine göre dünün tarihini döndürür."""
    now_turkey = datetime.now(TURKEY_TZ)
    yesterday = now_turkey - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")


def get_yesterday_display():
    """Dünün Türkçe görüntüleme tarihini döndürür."""
    gun_isimleri = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
    ay_isimleri = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
                   "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    
    now_turkey = datetime.now(TURKEY_TZ)
    yesterday = now_turkey - timedelta(days=1)
    
    gun = gun_isimleri[yesterday.weekday()]
    ay = ay_isimleri[yesterday.month - 1]
    return f"{yesterday.day} {ay} {yesterday.year} • {gun}"


def fetch_news_from_claude(date_str: str) -> list:
    """
    Claude API kullanarak belirtilen tarihteki en önemli 15 haberi toplar.
    Web search tool ile güncel haberleri çeker.
    """
    client = anthropic.Anthropic()  # ANTHROPIC_API_KEY env'den otomatik alınır

    prompt = f"""Bugün {date_str} tarihli haberleri derliyorum. 
Lütfen {date_str} tarihinde yayınlanmış en önemli 15 teknolojiyle ilgili haberi bul.

Kategoriler:
- ai (Yapay Zeka): 5 haber
- marketing (Pazarlama/Dijital Pazarlama): 4 haber  
- software (Yazılım & Teknoloji): 3 haber
- finance (Finans/Borsa/Ekonomi): 3 haber

SADECE aşağıdaki JSON formatında yanıt ver, başka hiçbir şey yazma:

[
  {{
    "num": "01",
    "cat": "ai",
    "title": "Haber başlığı (Türkçe, kısa ve çarpıcı)",
    "desc": "1-2 cümlelik Türkçe açıklama",
    "url": "https://kaynak-url.com/makale",
    "source": "KAYNAK ADI"
  }},
  ...
]

Kurallar:
- Tüm başlıklar ve açıklamalar Türkçe olmalı
- URL'ler gerçek ve erişilebilir olmalı
- Haberler gerçekten {date_str} tarihinde yayınlanmış olmalı
- num alanı 01'den 15'e kadar sıralı olmalı
- Öncelik sırası: önem derecesine göre
- JSON dışında hiçbir metin yazma, markdown backtick kullanma"""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4000,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        messages=[{"role": "user", "content": prompt}]
    )

    # Yanıttan JSON'u çıkar
    full_text = ""
    for block in message.content:
        if hasattr(block, "text"):
            full_text += block.text

    # JSON array'i bul ve parse et
    json_match = re.search(r'\[[\s\S]*\]', full_text)
    if not json_match:
        raise ValueError(f"Claude yanıtından JSON çıkarılamadı:\n{full_text[:500]}")

    news_list = json.loads(json_match.group())
    
    # Validasyon
    required_keys = {"num", "cat", "title", "desc", "url", "source"}
    valid_cats = {"ai", "marketing", "software", "finance"}
    
    validated = []
    for item in news_list[:15]:
        if not all(k in item for k in required_keys):
            continue
        if item["cat"] not in valid_cats:
            continue
        # Tırnak ve özel karakterleri escape et
        item["title"] = item["title"].replace('"', '\\"').replace("\n", " ")
        item["desc"] = item["desc"].replace('"', '\\"').replace("\n", " ")
        validated.append(item)

    if len(validated) < 10:
        raise ValueError(f"Yeterli haber bulunamadı: {len(validated)} haber")

    print(f"✅ {len(validated)} haber başarıyla toplandı")
    return validated


def format_news_js(date_str: str, news_list: list) -> str:
    """Haber listesini JavaScript nesne formatına çevirir."""
    items = []
    for item in news_list:
        items.append(
            f'    {{ num: "{item["num"]}", cat: "{item["cat"]}", '
            f'title: "{item["title"]}", '
            f'desc: "{item["desc"]}", '
            f'url: "{item["url"]}", '
            f'source: "{item["source"]}" }}'
        )
    return f'  "{date_str}": [\n' + ',\n'.join(items) + '\n  ]'


def update_html(date_str: str, news_list: list):
    """index.html dosyasını yeni haberlerle günceller."""
    
    with open(SITE_FILE, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Yeni günün haberlerini ekle
    new_entry = format_news_js(date_str, news_list)
    
    # newsDatabase objesine yeni gün ekle
    marker = "// Yeni günler buraya eklenecek:"
    if marker in html:
        # Mevcut arşivin sonuna ekle
        html = html.replace(
            marker,
            f"{new_entry},\n  {marker}"
        )
    else:
        # Fallback: newsDatabase'in kapanış parantezinden önce ekle
        html = html.replace(
            "\n};",
            f",\n{new_entry}\n}};",
            1
        )

    # 2. Varsayılan seçili tarihi güncelle
    # selectedDate'i yeni tarihe çek
    html = re.sub(
        r'selectedDate = "[0-9-]+"',
        f'selectedDate = "{date_str}"',
        html
    )

    # 3. Hero tarih badge'ini güncelle
    display_date = get_yesterday_display()
    html = re.sub(
        r'<div class="date-badge" id="heroDate">[^<]+</div>',
        f'<div class="date-badge" id="heroDate">{display_date}</div>',
        html
    )

    # 4. today değişkenini güncelle (bugünün tarihi)
    now_turkey = datetime.now(TURKEY_TZ)
    html = re.sub(
        r'const today = new Date\(\d+, \d+, \d+\)',
        f'const today = new Date({now_turkey.year}, {now_turkey.month - 1}, {now_turkey.day})',
        html
    )

    # 5. Eski arşivi temizle (MAX_ARCHIVE_DAYS'den eski)
    cutoff = datetime.now(TURKEY_TZ) - timedelta(days=MAX_ARCHIVE_DAYS)
    cutoff_str = cutoff.strftime("%Y-%m-%d")
    
    # Eski tarihleri regex ile bul ve sil
    pattern = r'  "\d{4}-\d{2}-\d{2}": \[[\s\S]*?\],?\n'
    matches = re.finditer(pattern, html)
    for match in matches:
        date_match = re.search(r'"(\d{4}-\d{2}-\d{2})"', match.group())
        if date_match and date_match.group(1) < cutoff_str:
            html = html.replace(match.group(), "")
            print(f"🗑️ Eski arşiv silindi: {date_match.group(1)}")

    # Dosyayı kaydet
    with open(SITE_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ {SITE_FILE} güncellendi: {date_str}")


def main():
    print("=" * 50)
    print("📰 Dünün Teknoloji Haberleri - Güncelleme")
    print("=" * 50)

    date_str = get_yesterday_date()
    display = get_yesterday_display()
    print(f"📅 Tarih: {display} ({date_str})")

    # API key kontrolü
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY bulunamadı!")
        print("   GitHub repo Settings → Secrets → ANTHROPIC_API_KEY ekleyin")
        exit(1)

    # HTML dosyası kontrolü
    if not os.path.exists(SITE_FILE):
        print(f"❌ {SITE_FILE} bulunamadı!")
        exit(1)

    # Aynı tarih zaten var mı kontrol et
    with open(SITE_FILE, "r", encoding="utf-8") as f:
        if f'"{date_str}"' in f.read():
            print(f"⚠️ {date_str} zaten mevcut, atlanıyor.")
            return

    # Haberleri topla
    print("🔍 Haberler toplanıyor...")
    news = fetch_news_from_claude(date_str)

    # HTML'i güncelle
    print("📝 Site güncelleniyor...")
    update_html(date_str, news)

    print("=" * 50)
    print("🎉 Güncelleme tamamlandı!")
    print(f"   {len(news)} haber eklendi: {date_str}")
    print("=" * 50)


if __name__ == "__main__":
    main()
