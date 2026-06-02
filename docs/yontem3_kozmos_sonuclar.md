# Yöntem 3 — KOZMOS (YTÜ) ile ABSA: Sonuç Raporu

**Branch:** `yontem_cozmos` · **Sorumlu:** Ahmet Çağlar
**Model:** `ytu-ce-cosmos/turkish-small-bert-uncased`
**Görev:** Aspect-Based Duygu Analizi (yorum + aspect → pozitif / negatif / nötr)

---

## 1. Deney Kurulumu

| Bileşen | Değer |
|---|---|
| Girdi formatı | `{yorum} [SEP] {aspect}` |
| Sınıflar | negatif (0), nötr (1), pozitif (2) |
| Maksimum uzunluk | 128 token |
| Optimizasyon | AdamW, lr=2e-5, weight_decay=0.01, warmup_ratio=0.1 |
| Epoch | maks. 10, early stopping (patience=2, `macro_f1`) → **7. epoch'ta durdu** |
| Batch | train 16, eval 32, fp16 |
| Sınıf dengesizliği | `balanced` class weight (notr ≈ 4.06, negatif ≈ 0.97, pozitif ≈ 0.58) ile ağırlıklı CrossEntropy |

**Veri:** Train 2.350 · Validation 504 · Test 504 (stratified, `random_state=42`).
Eğitim setinde sentiment dağılımı pozitif 1.347 · negatif 810 · nötr 193 — nötr
sınıfı belirgin biçimde az temsil ediliyor, raporun ana kısıtı bu.

---

## 2. Genel Sonuçlar (Test, 504 örnek)

| Metrik | Değer |
|---|---|
| **Accuracy** | **%79,37** |
| **Macro F1** | **0,63** |
| Weighted F1 | 0,79 |

### Sınıf bazlı

| Sınıf | Precision | Recall | F1 | Destek |
|---|---|---|---|---|
| pozitif | 0,87 | 0,86 | 0,87 | 289 |
| negatif | 0,77 | 0,82 | 0,79 | 174 |
| **nötr** | **0,26** | **0,22** | **0,24** | 41 |

> Pozitif ve negatif sınıflar güçlü (F1 0,87 ve 0,79). Genel doğruluğu aşağı çeken
> tek faktör nötr sınıfı: 41 örneğin yalnızca 9'u doğru sınıflandırılmış.
> İlgili görsel: `visuals/kozmos_visuals/02_sinif_metrikleri.png`

---

## 3. Karmaşıklık Matrisi

Satır = gerçek etiket, sütun = tahmin (`visuals/kozmos_visuals/01_karmasiklik_matrisi.png`):

| Gerçek ↓ / Tahmin → | pozitif | negatif | nötr | Toplam | Recall |
|---|---|---|---|---|---|
| **pozitif** | 249 | 25 | 15 | 289 | %86,2 |
| **negatif** | 22 | 142 | 10 | 174 | %81,6 |
| **nötr** | 15 | 17 | 9 | 41 | %22,0 |
| **Tahmin toplamı** | 286 | 184 | 34 | 504 | |

**Okunan bulgular:**
- **Nötr çöküyor:** 41 nötr örneğin 32'si kutuplu sınıflara kaçıyor (15 pozitif, 17 negatif). Model nötr için yalnızca 34 tahmin üretmiş (gerçek 41) — sınıfı sistematik olarak az tahmin ediyor.
- **Kutuplu karışım dengeli ve düşük:** pozitif↔negatif karışması simetrik (25 ve 22) ve sınırlı; ciddi bir yön hatası yok.
- Class weight nötr'ü tamamen kurtaramamış; veri azlığı baskın. Ağırlık olmasaydı nötr recall'ı muhtemelen sıfıra yakın olurdu, dolayısıyla kısmî fayda sağlamış.

---

## 4. Aspect Bazlı Doğruluk

`visuals/kozmos_visuals/05_aspect_dogruluk.png` — kırmızı çizgi genel doğruluk (%79,4):

| Aspect | n | Doğruluk | Yorum |
|---|---|---|---|
| batarya | 33 | **%93,9** | Çoğu negatif (24/33); net kutuplu dil, kolay |
| kalite | 67 | %89,6 | Açık "orijinal/bozuk" ifadeleri, nötr neredeyse yok (1) |
| ambalaj | 50 | %88,0 | "sağlam/özensiz" kalıpları ayırt edici |
| kargo | 51 | %80,4 | Genel ortalama civarı |
| genel | 199 | %79,4 | En büyük grup, ortalamayı belirliyor |
| ses_goruntu | 59 | **%66,1** | Karışık duygu + 7 nötr; "iyi ama..." yapıları zorluyor |
| fiyat | 45 | **%60,0** | En zayıf; 9 nötr (%20) + fiyat-performans ifadeleri belirsiz |

**Örüntü:** Doğruluk, aspect içindeki nötr oranı ve duygu dengesi ile ters orantılı.
Tek yöne yatık aspect'ler (batarya→negatif, kalite→pozitif) kolay; nötrün yoğun
ve pozitif/negatifin dengeli olduğu **fiyat** ve **ses_goruntu** zorlu. "Fiyatına
göre iyi ama ses çıkmıyor" gibi karşıt-kutuplu cümleler tipik hata kaynağı.

---

## 5. Gerçek vs Tahmin Dağılımı

`visuals/kozmos_visuals/06_gercek_vs_tahmin.png`:

| Sınıf | Gerçek | Tahmin |
|---|---|---|
| pozitif | 289 | 286 |
| negatif | 174 | 184 |
| nötr | 41 | 34 |

Model pozitifi neredeyse birebir, negatifi hafif fazla (+10), nötrü eksik (−7)
tahmin ediyor. Kaybolan nötrler ağırlıkla negatife yazılıyor (matris: 17 nötr→negatif).

---

## 6. Sonuç ve Notlar

- KOZMOS, küçük (small) bir Türkçe BERT olmasına rağmen pozitif/negatif ayrımında
  güçlü (F1 0,87 / 0,79) ve **%79,4 genel doğruluk** veriyor. Eğitim 7 epoch'ta
  ~76 saniyede tamamlandı (T4) — hafif ve hızlı.
- **Ana kısıt nötr sınıfının veri azlığı** (train'de 193, test'te 41). Class weight
  kısmî yardım etti ama F1'i 0,24'ün üzerine çıkaramadı. İyileştirme yönü: nötr
  örneklerini artırmak (veri toplama/augmentation) veya nötr'ü ayrı eşikle ele almak.
- Aspect bazlı kırılım, modelin **fiyat** ve **ses/görüntü** gibi karşıt-kutuplu
  ifadelerin yoğun olduğu boyutlarda zorlandığını gösteriyor; bu, ABSA'nın bütünsel
  duygu analizine göre neden daha zor olduğunun somut kanıtı.

### Üretilen görseller (`visuals/kozmos_visuals/`)
1. `01_karmasiklik_matrisi.png` — karmaşıklık matrisi (sayı + %)
2. `02_sinif_metrikleri.png` — sınıf bazlı precision/recall/F1
3. `03_aspect_frekanslari.png` — test setinde aspect dağılımı
4. `04_aspect_sentiment_tahmin.png` — aspect başına tahmin edilen duygu
5. `05_aspect_dogruluk.png` — aspect bazlı doğruluk
6. `06_gercek_vs_tahmin.png` — gerçek vs tahmin duygu dağılımı

### Çıktılar
- Tahminler: `data/predictions/kozmos_predictions.csv` (504 satır: yorum, aspect, sentiment, tahmin)
- Notebook: `notebooks/03_yontem_kozmos.ipynb`

> **3 model karşılaştırması** (Kural Tabanlı · BERTürk · KOZMOS) tüm modeller
> tamamlandığında ayrı bir dokümanda birleştirilecektir.
