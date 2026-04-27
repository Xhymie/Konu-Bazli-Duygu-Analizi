# E-Ticaret Yorumlarında Aspect-Based Duygu Analizi
 
> Trendyol elektronik kategorisindeki kullanıcı yorumlarından ürün boyutlarını (kargo, kalite, fiyat, batarya, ses/görüntü, ambalaj, müşteri hizmetleri) tespit ederek her boyut için duygu sınıflandırması yapan veri madenciliği projesi.
 
## İçindekiler
 
- [Proje Hakkında](#proje-hakkında)
- [Problem Tanımı](#problem-tanımı)
- [Veri Kaynakları](#veri-kaynakları)
- [Yöntem](#yöntem)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [Sonuçlar](#sonuçlar)
- [Ekip](#ekip)
- [Kaynakça](#kaynakça)
 
## Proje Hakkında
 
Bu proje, Kocaeli Üniversitesi Yazılım Mühendisliği 4.Sınıf **Veri Madenciliği** dersi dönem projesi kapsamında hazırlanmıştır. Geleneksel duygu analizinin ötesine geçerek, bir ürün yorumundaki **farklı boyutlara (aspect)** yönelik duyguları ayrı ayrı tespit etmeyi amaçlamaktadır.
 
Örnek:
> *"Telefonun kamerası harika ama batarya bir günü bile zor götürüyor, kargo hızlıydı."*
> - Kamera → **Pozitif**
> - Batarya → **Negatif**
> - Kargo → **Pozitif**
 
## Problem Tanımı
 
E-ticaret platformlarındaki ürün yorumları, tek bir yıldız puanıyla özetlenemeyecek kadar zengin bilgi içerir. Bir kullanıcı ürünün kalitesinden memnun olurken kargo hizmetinden şikayetçi olabilir. Geleneksel duygu analizi yöntemleri yorumu bütünsel olarak değerlendirdiğinden bu ayrımı yakalayamaz.
 
**Araştırma Sorusu:** E-ticaret yorumlarındaki farklı elektronik ürünlerdeki (kargo, kalite, fiyat, batarya, ses/görüntü) otomatik olarak tespit edilebilir mi ve her boyut için duygu sınıflandırması ne düzeyde doğrulukla yapılabilir?
 
**Hedef Çıktılar:**
- Aspect tespit modeli (yorumda hangi konudan bahsediliyor?)
- Aspect bazlı duygu sınıflandırma modeli (her boyut için pozitif/negatif/nötr)
- Klasik ML ve transfer learning (BERTurk) yaklaşımlarının karşılaştırmalı analizi
 
## Veri Kaynakları
 
| Kaynak | Tür | Açıklama |
|--------|-----|----------|
| **Trendyol** (birincil) | Web Scraping | Elektronik kategorisindeki ürün yorumları, yıldız puanları, tarih bilgileri |
| **Kaggle Türkçe Yorum Datasetleri** (ikincil) | Açık Veri | Cross-domain doğrulama ve model genellenebilirlik testi için |
 
- **Erişim Yöntemi:** Selenium ile otomatik tarayıcı kontrolü (Puan filtresi otomasyonu dahil). Detaylar için bkz. `docs/scraping_notes.md`.
- **Hedef Ürün Grupları:** 6 elektronik ürün — 2 telefon (iPhone 13, iPhone 11), 2 kulaklık (AirPods 2/4), 2 bilgisayar (MacBook Air M1, Lenovo IdeaPad Slim 3).
- **Toplanan Değişkenler:** Yorum metni, yıldız puanı (1-5), yorum tarihi, ürün adı, satıcı adı, beğeni sayısı.
- **Toplam Yorum Sayısı:** 1500 (ürün başına 250). 1, 2, 3, 4 yıldız için her birinden ~50 yorum, kalan kota 5 yıldızdan tamamlanmıştır (dengeli sentiment dağılımı için).
- **Etiketleme:** Aspect bazlı anahtar kelime sözlüğü ile otomatik etiketleme + manuel doğrulama

### Veri Dağılımı

| Puan | Sayı | Yüzde |
|------|------|-------|
| 1    | 300  | %20   |
| 2    | 163  | %11   |
| 3    | 238  | %16   |
| 4    | 300  | %20   |
| 5    | 499  | %33   |
 
## Yöntem
 
### Veri Toplama & Ön İşleme
- Selenium tabanlı web scraper ile Trendyol'dan dengeli veri toplama
- Trendyol'un puan filtresi otomasyonu (1-5 yıldız ayrı ayrı çekilir)
- Otomatik aspect ve sentiment etiketleme (anahtar kelime sözlüğü)
- Detaylı teknik notlar: `docs/scraping_notes.md`
 
### Modelleme Yaklaşımları
- **Baseline:** TF-IDF + Logistic Regression / Linear SVM (planlanıyor)
- **Transfer Learning:** BERTurk fine-tuning (planlanıyor)
- **Görevler:** Sentiment classification (3 sınıf), Rating prediction (5 sınıf), Aspect classification (multi-label)

### Değerlendirme Metrikleri
- Accuracy, Precision, Recall, F1-Score (aspect bazlı ve genel)
- Confusion Matrix
- ROC-AUC (çoklu sınıf)
 
## Proje Yapısı
- Şuanlık proje yapısı oluşturuldu, oluşturulacak yeni dosyalar ya da alt dizinler buraya eklenecektir.
 
``
/
├── README.md                                    # Proje açıklaması
├── requirements.txt                             # Python bağımlılıkları
├── .gitignore                                   # Git dışı tutulan dosyalar
│
├── data/
│   ├── raw/                                     # İşlenmemiş veri
│   │   └── trendyol_yorumlar_dengeli.csv        # 1500 yorum, 6 ürün
│   └── processed/                               # Temizlenmiş ve etiketli veri
│
├── src/
│   └── scrape_trendyol.py                       # Trendyol scraper (Selenium)
│
├── notebooks/                                   # Jupyter notebookları (EDA, modelleme)
├── visuals/                                     # Grafikler ve görseller
├── reports/                                     # Raporlar (ara/final)
└── docs/
    └── scraping_notes.md                        # Scraping teknik dokümantasyonu
```
 
## Kurulum
 
```bash
# Repo'yu klonlayın
git clone https://github.com/Xhymie/Konu-Bazli-Duygu-Analizi.git
cd Konu-Bazli-Duygu-Analizi
 
# Sanal ortam oluşturun
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
 
# Bağımlılıkları yükleyin (şuanlık bir şey yok)
pip install -r requirements.txt
```
 
## Kullanım
 
### Veri toplama (yeniden çekmek isteyenler için)

```bash
python src/scrape_trendyol.py
```

> Scraper Chrome tarayıcıyı görünür modda açar. ~15 dakika sürer ve `trendyol_yorumlar_dengeli.csv` üretir. Toplama işlemi tamamlandığında dosya manuel olarak `data/raw/` altına taşınmalıdır.

### Veri keşfi

```bash
Mevcut CSV ile çalışmak için doğrudan data/raw/trendyol_yorumlar_dengeli.csv kullanın
```

Modelleme bölümleri eklendikçe bu kısım güncellenecektir.


 
## Sonuçlar
 
### Veri Toplama (Tamamlandı)
- 6 elektronik ürün için 1500 yorum
- Puan dağılımı dengeli (eskiden %80 5⭐ iken şimdi %33)
- HTML parse'tan gelen rating ile filter rating %100 uyumlu

### Modelleme (Devam Ediyor)
> Sonuçlar elde edildikçe bu bölüm güncellenecektir.
 
## Ekip

| İsim | Görev Alanı |
|------|-------------|
| Ahmet Çağlar | Görev Alanı dağıtılmadı, yapıldıkça commitle beraber buralarda güncellenecektir. |
| İbrahim Biner | Görev Alanı dağıtılmadı, yapıldıkça commitle beraber buralarda güncellenecektir. |
| Dilara Çatalçam | Veri toplama (scraper geliştirme), veri kalite kontrolü. | |
 
## Kaynakça
 
- Örnek kaynakça burada tutulacaktır. Her referansta burasıda update edilip belirtilecektir.
