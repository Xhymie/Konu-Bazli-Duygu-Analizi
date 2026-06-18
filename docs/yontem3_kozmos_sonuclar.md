# Yöntem 3 — KOZMOS (YTÜ) ile ABSA: Sonuç ve Değerlendirme Raporu

**Branch:** `yontem_cozmos` · **Sorumlu:** Ahmet Çağlar
**Model:** `ytu-ce-cosmos/turkish-small-bert-uncased`
**Görev:** Aspect-Based Duygu Sınıflandırma (yorum + aspect → pozitif / negatif / nötr)

> Sayılar, **yorum bazlı (group) split** ve **sabit seed (42)** ile üretilen tek koşudandır.
> Split leakage içermez (test–train yorum örtüşmesi %0). Çok-seed ortalaması ileride eklenebilir.

---

## 1. Deney Kurulumu

| Bileşen | Değer |
|---|---|
| Girdi formatı | `{yorum} [SEP] {aspect}` (Sun et al. 2019, auxiliary-sentence yaklaşımı) |
| Sınıflar | negatif (0), nötr (1), pozitif (2) |
| Maksimum uzunluk | 128 token |
| Optimizasyon | AdamW, lr=2e-5, weight_decay=0.01, warmup_ratio=0.1 |
| Epoch | maks. 10, early stopping (patience=2, `macro_f1`) |
| Sınıf dengesizliği | `balanced` class weight ile ağırlıklı CrossEntropy |
| Split | **GroupShuffleSplit (yorum bazlı)**, seed=42 → Train 2342 / Val 506 / Test 510 |
| Donanım | Google Colab T4, fp16 |

Sentiment dağılımı dengesiz: pozitif ~%59, negatif ~%32, nötr ~%9.

---

## 2. Genel Sonuçlar (Test, 510 örnek)

| Metrik | Değer | Not |
|---|---|---|
| Accuracy | **%80.6** | İkincil metrik (dengesiz dağılımda yanıltıcı) |
| **Macro F1** | **0.657** | **Birincil metrik** |
| Majority baseline (hep "pozitif") | %59.8 | KOZMOS bunu ~21 puan geçiyor |

### Sınıf bazlı

| Sınıf | Precision | Recall | F1 | Destek |
|---|---|---|---|---|
| pozitif | 0.89 | 0.88 | 0.88 | 305 |
| negatif | 0.72 | 0.83 | 0.77 | 160 |
| **nötr** | **0.46** | **0.24** | **0.32** | 45 |

Model pozitif/negatif ayrımında baseline'ı belirgin biçimde aşıyor. Genel başarıyı sınırlayan
nötr sınıfıdır: precision yükselmiş (0.46) ama recall düşük (0.24) — model nötr'ü temkinli
tahmin ediyor, çoğunu kaçırıyor. Bu, az temsil (n=45) ve nötr'ün anotasyon öznelliğinin sonucu.

---

## 3. Karmaşıklık Matrisi

| Gerçek ↓ / Tahmin → | pozitif | negatif | nötr | Recall |
|---|---|---|---|---|
| pozitif | 267 | 33 | 5 | %87.5 |
| negatif | 19 | 133 | 8 | %83.1 |
| nötr | 14 | 20 | 11 | %24.4 |

Nötr örnekler çoğunlukla kutuplu sınıflara dağılıyor (14 pozitif, 20 negatif). Kutuplu
sınıflar arası karışım düşük ve simetrik.

---

## 4. Aspect Bazlı Doğruluk

| Aspect | n | Doğruluk |
|---|---|---|
| kalite | 52 | %92.3 |
| genel | 226 | %85.0 |
| ambalaj | 45 | %82.2 |
| kargo | 59 | %76.3 |
| ses_goruntu | 50 | %72.0 |
| fiyat | 42 | %69.0 |
| batarya | 36 | %66.7 |

> Aspect başına örnek sayıları küçüktür (36–226); bu oranlar kesin başarı değil **eğilim**
> olarak okunmalıdır. Tek-kutuplu aspect'ler (kalite) kolay; nötr ve karşıt-kutuplu
> ifadelerin yoğunlaştığı boyutlar (fiyat, batarya) görece zor.

---

## 5. Aspect Duyarlılığı: Model aspect'i gerçekten kullanıyor mu?

Group split, bir yorumun tüm aspect satırlarını aynı bölmede tuttuğu için çok-aspect'li
yorumlar test'te bütün halde yer alır. Bu sayede aspect-çakışan (aynı yorumda farklı duygu)
örnekler **31 yoruma** çıktı ve aspect-duyarlılığı sağlam ölçülebildi:

- Aspect-çakışan 31 yorum (76 satır) doğruluğu **%55.3** — genel %80.6'nın belirgin altında.
- Model bu 31 yorumun **yalnızca 3'ünde** aspect'e göre tahminini değiştirdi (flip 3/31).

**Sonuç:** Model büyük ölçüde **cümle-düzeyi duygu** üretiyor; gerçek aspect-koşullama zayıf.
Tek-duygulu yorumlarda başarılı, ama tek cümlede iki aspect çelişince baskın duyguya yöneliyor.
Yöntem (girdi formatı) standarttır; sınır, verinin çakışan örnek bakımından seyrek olmasıdır
(eğitim setinde bu tür yorumlar azınlıktadır).

---

## 6. Veri Sızıntısı ve Yeniden Üretilebilirlik

- **Leakage çözüldü:** Önceki satır bazlı split'te test yorumlarının ~%50'si train'de de
  görünüyordu. Yorum bazlı (GroupShuffleSplit) geçişle bu oran **%0**'a kadar indi; bildirilen
  doğruluk artık gerçek genelleme tahminidir.
- **Tekrarlanabilirlik:** Eğitimde sabit seed (42) kullanıldı. Sonuç yine de tek koşudur;
  güven aralığı için çok-seed ortalaması önerilir.
- **Diğer sınırlar:** Nötr sınıf veri azlığı (n=45) nedeniyle güvenilmez; aspect başına ve
  çakışan örnek sayıları küçük olduğundan ilgili oranlar temkinle okunmalıdır.

---

## 7. Açıklanabilirlik: Yorumlayıcı Ön Analiz

Modelin kararını hangi kelimelere dayandığını incelemek için iki araç kullanıldı:

- **Attention görünümü:** Attention ağırlıkları büyük ölçüde `[SEP]`/`[CLS]` üzerine
  yoğunlaştığından (attention sink), ham attention tek başına açıklama sayılmamalıdır
  (Jain & Wallace, 2019).
- **Integrated Gradients (Captum):** Her kelimenin tahmine katkısını gösterir; baseline
  olarak `[CLS]/[SEP]` korunup içerik token'ları `[PAD]`'e indirildi.

Tek-kutuplu yorumlarda IG doğru duygu kelimelerini öne çıkarıyor; karşıt-kutuplu yorumlarda
model sorgulanan aspect'ten bağımsız olarak baskın kelimeye yöneliyor — bu, §5'teki
cümle-düzeyi davranış bulgusunu destekler. Bu bölüm seçilmiş örneklere dayanan **niteliksel
ön analizdir**, nicel açıklanabilirlik iddiası taşımaz.

---

## 8. Genel Değerlendirme

KOZMOS, küçük ve hızlı bir Türkçe BERT olarak pozitif/negatif ayrımında baseline'ı net aşan
(%80.6 doğruluk, macro F1 0.657), **leakage'sız ve tekrarlanabilir** bir prototiptir. Nötr
sınıfta ve gerçek aspect-duyarlılığında sınırlıdır (flip 3/31). Çalışmanın değeri, bu sınırları
kendi verisi üzerinde ölçüp belgelemesidir.

### Çıktılar
- Tahminler: `data/predictions/kozmos_predictions.csv` (510 satır)
- Görseller: `visuals/kozmos_visuals/`
- Notebook: `notebooks/03_yontem_kozmos.ipynb`

> 3 yöntemin (Kural Tabanlı · BERTürk · KOZMOS) karşılaştırması, tüm modeller tamamlandığında
> **aynı group-based split** üzerinde ayrı bir dokümanda yapılacaktır.
