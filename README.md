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
 
- **Erişim Yöntemi:** Buna belirlenip bu kısım güncellenecektir.
- **Hedef Ürün Grupları:** Akıllı telefon, pc, bluetooth kulaklık vb elektronik araçlar.
- **Toplanacak Tahmini Değişkenler:** Yorum metni, yıldız puanı (1-5), yorum tarihi, ürün adı, satıcı adı, beğeni sayısı
- **Etiketleme:** Aspect bazlı anahtar kelime sözlüğü ile otomatik etiketleme + manuel doğrulama
 
## Yöntem
 
### Veri Toplama & Ön İşleme
- 
 
### Modelleme Yaklaşımları
-
 
### Değerlendirme Metrikleri
- Accuracy, Precision, Recall, F1-Score (aspect bazlı ve genel)
- Confusion Matrix
- ROC-AUC (çoklu sınıf)
 
## Proje Yapısı
- Şuanlık proje yapısı oluşturuldu, oluşturulacak yeni dosyalar ya da alt dizinler buraya eklenecektir.
 
```
/
├── README.md                    # Proje açıklaması ve güncellendiğinde update edilecektir.
├── requirements.txt             # Python bağımlılıkları ve kütüphaneler için yazılacaktır.
├── .gitignore                   # Git dışı tutulan dosyalar.
├── data/
├── notebooks/
├── src/
├── visuals/
├── reports/
└── docs/
    
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
 
Bu kısım proje yapıldıkça güncellenecektir.
 
## Sonuçlar
 
> Proje devam etmektedir. Sonuçlar elde edildikçe bu bölüm güncellenecektir.
 
## Ekip
 
| İsim | Görev Alanı |
|------|-------------|
| Ahmet Çağlar | Görev Alanı dağıtılmadı yapıldıkça commitle beraber buralarda güncellenecektir. |
| İbrahim Biner | Görev Alanı dağıtılmadı yapıldıkça commitle beraber buralarda güncellenecektir.  |
| Dilara Çatalçam | Görev Alanı dağıtılmadı yapıldıkça commitle beraber buralarda güncellenecektir. |
 
## Kaynakça
 
- Örnek kaynakça burada tutulacaktır. Her referansta burasıda update edilip belirtilecektir.