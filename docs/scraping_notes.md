# Veri Toplama Notları (Trendyol Scraping)

Bu doküman, Trendyol'dan yorum verilerini toplarken karşılaşılan teknik
sorunları ve çözümlerini içerir. İleride başka bir e-ticaret sitesi için
benzer bir scraper yazılması durumunda referans olarak kullanılabilir.

## Karşılaşılan Sorunlar ve Çözümler

### 1. API erişimi engelli

İlk yaklaşım Trendyol'un public review API'sini kullanmaktı
(`/Discovery/web/api/Reviews/...`). Ancak bu endpoint Cloudflare ile
korunuyor ve Python `requests` ile erişimde **403 Forbidden** dönüyor.

**Çözüm:** Selenium ile gerçek bir Chrome tarayıcı üzerinden scraping.

### 2. Yorum sayfasında pagination yok

Trendyol'un yorum sayfası klasik sayfalama (sayfa 1, 2, 3 ...) kullanmıyor.
Bunun yerine **infinite scroll** yapısı var — sayfa aşağı kaydırıldıkça
yeni yorumlar dinamik olarak yükleniyor.

**Çözüm:** `window.scrollTo(0, document.body.scrollHeight)` ile sayfanın
en altına scroll edip yeni içerik için 2-3 saniye bekleme. Aynı yorum
sayısı 3 kez ardışık tekrar ederse "yeni yorum gelmiyor" kabul edilip
durduruluyor.

### 3. Headless modda davranış değişiyor

Chrome `--headless` modunda açıldığında scroll davranışı düzgün çalışmıyor,
yorumlar yüklenmiyor.

**Çözüm:** Görünür modda çalıştırılıyor (`HEADLESS = False`). Pencere
arka planda açık kalıyor ama kullanıcıyı rahatsız etmiyor.

### 4. Düşük puanlı yorumlar yetersiz

Trendyol varsayılan olarak "Önerilen Sıralama" kullanıyor; bu da yüksek
puanlı (4-5 yıldız) yorumları öne atıyor. Sadece scroll ile veri çekildiğinde
veri setinin %80'inden fazlası 5 yıldızlı yorumlardan oluşuyor — sentiment
analizi için kötü bir dengesizlik.

**Çözüm:** Sayfadaki **"Puan" filtre dropdown'u** otomatik olarak açılıp
1, 2, 3, 4, 5 yıldız checkbox'ları sırayla seçiliyor. Her puan için ayrı
ayrı scrape yapılıp sonuçlar birleştiriliyor.

İlgili HTML yapısı:

```html
<button data-testid="filter-toggle-rate">Puan</button>     <!-- Dropdown'u açar -->

<div data-testid="filter-items-list-rate">
  <label>5 yıldız checkbox</label>     <!-- Sıra: 5,4,3,2,1 -->
  <label>4 yıldız checkbox</label>
  <label>3 yıldız checkbox</label>
  <label>2 yıldız checkbox</label>
  <label>1 yıldız checkbox</label>
</div>

<button data-testid="filter-apply-button-rate">Uygula</button>
```

Önemli: Checkbox seçildikten sonra "Uygula" butonuna basılması gerekiyor;
yoksa filtre uygulanmıyor.

### 5. Dengesiz yorum dağılımı

Bazı ürünlerde 2-3 yıldızlı yorum sayısı çok düşük (örn. MacBook Air'de
sadece 4 adet 2 yıldızlı yorum var). Eşit kota (her puan için 50) uygulamak
toplam veri sayısını düşürüyor.

**Çözüm:** **Akıllı kota** sistemi. Önce 1-4 yıldız için 50 yorum hedeflenir
(bulunabildiği kadar). Eksik kalan miktar 5 yıldızlı yorumlardan tamamlanır.
Böylece her ürün için garantili 250 yorum elde edilirken negatif yorum
sayısı maksimize edilir.

### 6. Yıldız puanı parse hatası

Yorum kartlarında yıldız puanı görsel olarak `padding-inline-end` CSS
özelliği ile gösteriliyor:

| Puan | padding-inline-end |
|------|-------------------:|
| 5    | 0px                |
| 4    | 16.71px            |
| 3    | 33.43px            |
| 2    | 50.14px            |
| 1    | 66.86px            |

İlk denemede her yıldız 12.5px sanılmıştı — bu durumda 2 ve 3 yıldızlar
yanlış parse ediliyordu. Doğru bölen: **16.71** (gerçek değer dropdown
HTML'inden tespit edildi).

### 7. Tek seferlik DOM yüklenmeme glitch'i

Çok sayıda ardışık istek atıldığında Trendyol bazen sayfayı eksik render
ediyor (filtre butonları gelmiyor). Bu nadir ama gerçekleşiyor.

**Çözüm:** Bir puan için 0 yorum dönerse, 5 saniye beklenip **bir kez
daha deneniyor** (retry). Pratikte ikinci deneme her zaman başarılı.

## Selector Referansı (Trendyol)

Yorum sayfasının kritik CSS/data-testid yapıları:

| Element | Selector |
|---------|----------|
| Tüm yorumlar konteyneri | `div.review-list` |
| Tek yorum kartı | `div.review` |
| Yorum metni | `span.review-comment > span` |
| Kullanıcı adı | `div.detail-item.name` |
| Yorum tarihi | `div.detail-item.date` |
| Satıcı adı | `span.seller-name-wrapper strong` |
| Beğeni sayısı | `span.like-button-likes-count` |
| Yıldız (full) | `div.star-rating-full-star` |
| Puan filtresi açma | `button[data-testid='filter-toggle-rate']` |
| Yıldız checkbox listesi | `div[data-testid='filter-items-list-rate'] > label` |
| Filtre uygula | `button[data-testid='filter-apply-button-rate']` |
| Çerez kabul | `#onetrust-accept-btn-handler` |

## Anti-bot tedbirleri

Trendyol Selenium'a aşırı agresif değil, ama yine de bazı tedbirler alındı:

- `navigator.webdriver` `undefined` olarak override ediliyor
- `excludeSwitches: ["enable-automation"]` ayarı ile "automation" bayrağı kaldırılıyor
- Mac Chrome user-agent kullanılıyor (Linux varsayılan UA bazen şüphe çekiyor)
- Her ürün arasında 4 saniye, her puan filtresi arasında 4 saniye bekleme
- URL'lere timestamp parametresi (`?_=<timestamp>`) ekleniyor (cache bypass)

## Veri kalitesi

Toplam 1500 yorum çekildi (ürün başına 250). Filtreden gelen puan ile
HTML'den parse edilen puan **%100 uyumlu** (1500/1500). Veri seti dengeli:

| Puan | Sayı | Yüzde |
|------|------|-------|
| 1    | 300  | %20   |
| 2    | 163  | %11   |
| 3    | 238  | %16   |
| 4    | 300  | %20   |
| 5    | 499  | %33   |
