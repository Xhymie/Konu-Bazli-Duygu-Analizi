# E-Ticaret Yorumlarında Aspect-Based Duygu Analizi

> Trendyol elektronik kategorisindeki kullanıcı yorumlarından ürün boyutlarını (kargo, kalite, fiyat, batarya, ses/görüntü, ambalaj) tespit ederek her boyut için duygu sınıflandırması yapan veri madenciliği projesi.

## İçindekiler

- [Proje Hakkında](#proje-hakkında)
- [Problem Tanımı](#problem-tanımı)
- [Veri Kaynakları](#veri-kaynakları)
- [Aspect Tanımları](#aspect-tanımları)
- [Yöntemler](#yöntemler)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Sonuçlar](#sonuçlar)
- [Ekip](#ekip)
- [Kaynakça](#kaynakça)

## Proje Hakkında

Bu proje, Kocaeli Üniversitesi Yazılım Mühendisliği 4. Sınıf **Veri Madenciliği** dersi dönem projesi kapsamında hazırlanmıştır. Geleneksel duygu analizinin ötesine geçerek, bir ürün yorumundaki **farklı boyutlara (aspect)** yönelik duyguları ayrı ayrı tespit etmeyi amaçlamaktadır.

Örnek:
> *"Telefonun kamerası harika ama batarya bir günü bile zor götürüyor, kargo hızlıydı."*
> - Kamera → **Pozitif**
> - Batarya → **Negatif**
> - Kargo → **Pozitif**

## Problem Tanımı

E-ticaret platformlarındaki ürün yorumları, tek bir yıldız puanıyla özetlenemeyecek kadar zengin bilgi içerir. Bir kullanıcı ürünün kalitesinden memnun olurken kargo hizmetinden şikayetçi olabilir. Geleneksel duygu analizi yöntemleri yorumu bütünsel olarak değerlendirdiğinden bu ayrımı yakalayamaz.

**Araştırma Sorusu:** E-ticaret yorumlarındaki farklı aspect'ler (kargo, kalite, fiyat, batarya, ses/görüntü, ambalaj) otomatik olarak tespit edilebilir mi ve her boyut için duygu sınıflandırması ne düzeyde doğrulukla yapılabilir?

**Hedef Çıktılar:**
- Aspect bazlı duygu sınıflandırma modeli (her boyut için pozitif/negatif/nötr)
- Kural tabanlı, BERTürk ve KOZMOS yaklaşımlarının karşılaştırmalı analizi
- Aspect tespitini gösteren basit bir demo arayüzü (hoca önerisi)

## Veri Kaynakları

| Kaynak | Tür | Açıklama |
|--------|-----|----------|
| **Trendyol** (birincil) | Web Scraping | Elektronik kategorisindeki ürün yorumları, yıldız puanları, tarih bilgileri |

- **Erişim Yöntemi:** Selenium ile otomatik tarayıcı kontrolü (puan filtresi otomasyonu dahil). Detaylar için bkz. `docs/scraping_notes.md`.
- **Ürün Grupları:** 9 elektronik ürün — 3 kategori

| Kategori | Ürünler |
|----------|---------|
| Telefon (750 yorum) | iPhone 13, iPhone 11, Samsung Galaxy A24 |
| Kulaklık (750 yorum) | AirPods 2. Nesil, AirPods 4. Nesil, Redmi Buds 6 Play |
| Bilgisayar (750 yorum) | MacBook Air M1, Lenovo IdeaPad Slim 3, Casper Nirvana |

- **Toplam Ham Yorum:** 2.250 (ürün başına 250, dengeli yıldız dağılımı)
- **Toplanan Değişkenler:** Yorum metni, yıldız puanı (1–5), yorum tarihi, ürün adı, satıcı, beğeni sayısı

### Ham Veri — Yıldız Dağılımı

| Puan | Adet | Yüzde |
|------|------|-------|
| 1 ⭐  | ~300 | %13   |
| 2 ⭐  | ~163 | %7    |
| 3 ⭐  | ~238 | %11   |
| 4 ⭐  | ~300 | %13   |
| 5 ⭐  | ~499 | %22   |
| Dengeli çekim | — | %34 |

### Etiketli Veri

Etiketleme, hibrit kural tabanlı pipeline (`src/etiketle.py`) ile yapılmış ve manuel doğrulama ile desteklenmiştir.

| Dosya | İçerik | Satır |
|-------|--------|-------|
| `laptop_etiketli.csv` | Bilgisayar yorumları | 1.143 |
| `telefon_etiketli.csv` | Telefon yorumları | 1.056 |
| `kulaklik_etiketli.csv` | Kulaklık yorumları | 1.159 |
| `trendyol_yorumlar_etiketli.csv` | **Birleşik** (3 kategori) | **3.358** |

**Etiketli Veri Dağılımı:**

| Sentiment | Adet | Yüzde |
|-----------|------|-------|
| Pozitif | 1.925 | %57,3 |
| Negatif | 1.157 | %34,5 |
| Nötr | 276 | %8,2 |

| Aspect | Adet | Yüzde |
|--------|------|-------|
| genel | 1.436 | %42,8 |
| kargo | 386 | %11,5 |
| kalite | 380 | %11,3 |
| ses_goruntu | 368 | %11,0 |
| ambalaj | 285 | %8,5 |
| fiyat | 257 | %7,7 |
| batarya | 246 | %7,3 |

### Train / Validation / Test Ayrımı

Stratified split (sentiment dağılımı korunarak, `random_state=42`):

| Split | Satır | Oran |
|-------|-------|------|
| **Train** | 2.350 | %70 |
| **Validation** | 504 | %15 |
| **Test** | 504 | %15 |

Her split'te sentiment oranı sabit: Pozitif %57,3 · Negatif %34,5 · Nötr %8,2

## Aspect Tanımları

| Aspect | Açıklama |
|--------|----------|
| **genel** | Ürün hakkında genel değerlendirme, tavsiye/önermeme |
| **kargo** | Teslimat süreci, kurye, paketleme hızı |
| **kalite** | Ürün yapısı, dayanıklılık, orijinallik, fiziksel kusurlar |
| **fiyat** | Fiyat, fiyat-performans, kampanya |
| **batarya** | Pil ömrü, şarj süresi, ısınma |
| **ses_goruntu** | Ses kalitesi, kamera, ekran, görüntü |
| **ambalaj** | Paketleme, kutu durumu, ezilme/hasar |

## Yöntemler

### Yöntem 1 — Kural Tabanlı ABSA Tamamlandı (Tekrar yapılacak.)
**Branch:** `yontem_1` | **Sorumlu:** İbrahim Biner

- Türkçe aspect sözlüğü + sentiment analizi ile kural tabanlı ABSA pipeline
- Cümle bazlı aspect tespiti, negasyon yönetimi
- **Yöntem 1.5:** TF-IDF + sözlük hibrit yaklaşımı
- Değerlendirme: Accuracy, F1, Confusion Matrix, görselleştirmeler

### Yöntem 2 — BERTürk Fine-tuning Devam Ediyor
**Branch:** `yontem_2` | **Sorumlu:** Dilara Çatalçam

- Model: `dbmdz/bert-base-turkish-cased`
- Input formatı: `[CLS] {yorum} [SEP] {aspect} [SEP]`
- Fine-tuning: 3–5 epoch, Google Colab (GPU T4)
- Aynı metrikler + Yöntem 1 ile karşılaştırma

### Yöntem 3 — KOZMOS (YTÜ) Devam Ediyor
**Branch:** `yontem_cozmos` | **Sorumlu:** Ahmet Çağlar

- Model: `ytu-ce-cosmos/turkish-small-bert-uncased`
- YTÜ Bilgisayar Mühendisliği tarafından geliştirilen Türkçe BERT modeli
- Aynı test seti üzerinde değerlendirme → BERTürk ile karşılaştırma

### Karşılaştırma Tablosu (Dolacak)

| Metrik | Yöntem 1 | Yöntem 1.5 | Yöntem 2 (BERTürk) | Yöntem 3 (KOZMOS) |
|--------|----------|------------|---------------------|-------------------|
| Accuracy | — | — | — | — |
| Macro F1 | — | — | — | — |
| Pozitif F1 | — | — | — | — |
| Negatif F1 | — | — | — | — |
| Nötr F1 | — | — | — | — |

## Proje Yapısı

```
/
├── README.md
├── requirements.txt
├── .gitignore
│
├── data/
│   ├── raw/
│   │   └── trendyol_yorumlar_full.csv          # 2.250 ham yorum
│   ├── processed/
│   │   ├── laptop_etiketli.csv / .xlsx         # 1.143 etiketli çift
│   │   ├── telefon_etiketli.csv / .xlsx        # 1.056 etiketli çift
│   │   ├── kulaklik_etiketli.csv               # 1.159 etiketli çift
│   │   └── trendyol_yorumlar_etiketli.csv/.xlsx # 3.358 birleşik
│   └── split/
│       ├── train.csv                            # 2.350 satır (%70)
│       ├── val.csv                              # 504 satır (%15)
│       └── test.csv                             # 504 satır (%15)
│
├── src/
│   ├── scrape_trendyol.py                       # Scraping kodu
│   └── data_split.py                            # Stratified train/val/test
│
├── notebooks/
│   ├── 02_berturk_absa.ipynb                    # BERTürk (Dilara - Colab)
│   └── 03_kozmos_absa.ipynb                     # KOZMOS (Çağlar - Colab)
│
├── visuals/                                     # Grafikler
├── reports/                                     # Raporlar
└── docs/
    └── scraping_notes.md
```

## Kurulum

```bash
git clone https://github.com/Xhymie/Konu-Bazli-Duygu-Analizi.git
cd Konu-Bazli-Duygu-Analizi

python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt
```

## Sonuçlar

### Veri Toplama & Etiketleme

- 9 elektronik ürün, 3 kategori → 2.250 ham yorum
- Hibrit kural tabanlı etiketleme + manuel doğrulama
- 3.358 aspect-sentiment çifti, 2.217 benzersiz yorum
- Stratified train/val/test split (%70/%15/%15)

### Yöntem 1 — Kural Tabanlı

> Detaylar `yontem_1` branch'ında.

### Yöntem 2 & 3 — Derin Öğrenme

> Sonuçlar modeller tamamlandıkça buraya eklenecektir.

## Ekip

| İsim | Görev Alanı |
|------|-------------|
| **Ahmet Çağlar** | Web scraper geliştirme ve veri genişletme (+750 yorum). Telefon ve kulaklık yorumları için hibrit etiketleme pipeline'ı (`etiketle.py`). 3 kategorinin birleştirilmesi ve stratified train/val/test ayrımı. KOZMOS (YTÜ) modeli ile ABSA — `yontem_cozmos` branch. |
| **İbrahim Biner** | Laptop yorumları etiketlemesi. Kural tabanlı ABSA pipeline (Yöntem 1) ve TF-IDF hibrit yaklaşımı (Yöntem 1.5) — `yontem_1` branch. |
| **Dilara Çatalçam** | BERTürk (`dbmdz/bert-base-turkish-cased`) fine-tuning ile ABSA — `yontem_2` branch. EDA görselleştirmeleri ve model değerlendirmesi. |

## Kaynakça

> Kullanılan kaynaklar modelleme tamamlandıkça buraya eklenecektir.

---

## Hoca Revize Önerileri

| Öneri | Durum |
|-------|-------|
| Veri setini genişlet | 1.500 → 2.250 yorum (+750) |
| YTÜ KOZMOS modelini incele | `yontem_cozmos` branch'ında uygulanıyor |
| Aspect tespiti demo arayüzü | Modeller tamamlandıktan sonra |
