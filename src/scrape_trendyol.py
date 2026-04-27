"""
Trendyol Yorum Scraper - Selenium (v7 FINAL)
============================================
Trendyol'un gerçek HTML yapısı tespit edildi:

  <button data-testid="filter-toggle-rate">Puan</button>     ← dropdown'u açar
  <div data-testid="filter-items-list-rate">
    <label>5 yıldız checkbox</label>   ← sıra: 5,4,3,2,1
    <label>4 yıldız checkbox</label>
    ...
  </div>
  <button data-testid="filter-apply-button-rate">Uygula</button>   ← filtreyi uygular

Akış:
1. Yorum sayfasını aç
2. Puan butonuna tıkla → dropdown açılır
3. İstenen yıldıza ait checkbox label'ına tıkla
4. "Uygula" butonuna tıkla
5. Sayfa filtreli yorumları gösterir → scroll ile yükle
6. Bir sonraki puan için tekrarla

Kurulum:
    pip3 install selenium webdriver-manager beautifulsoup4 pandas

Kullanım:
    python3 trendyol_selenium.py
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from collections import Counter


# ─────────────────────────────────────────────
# ÜRÜN LİSTESİ
# ─────────────────────────────────────────────

URUN_LISTESI = [
    "https://www.trendyol.com/apple/iphone-13-128-gb-yildiz-isigi-cep-telefonu-apple-turkiye-garantili-p-150059024",
    "https://www.trendyol.com/apple/iphone-11-128-gb-beyaz-cep-telefonu-aksesuarsiz-kutu-apple-turkiye-garantili-p-64074794",
    "https://www.trendyol.com/apple/airpods-2-nesil-kulaklik-p-6405631",
    "https://www.trendyol.com/apple/airpods-4-nesil-mxp63tu-a-p-857508954",
    "https://www.trendyol.com/apple/macbook-air-m1-cip-8gb-256gb-ssd-macos-13-qhd-tasinabilir-bilgisayar-uzay-grisi-p-68042136",
    "https://www.trendyol.com/lenovo/ideapad-slim-3-intel-n100-4gb-ram-128gb-ssd-15-6-p-1057359906",
]

KATEGORI_MAP = {
    "150059024":  "Telefon",
    "64074794":   "Telefon",
    "6405631":    "Kulaklık",
    "857508954":  "Kulaklık",
    "68042136":   "Bilgisayar",
    "1057359906": "Bilgisayar",
}

# ════ AKILLI KOTA SİSTEMİ ════
# Hedef: ürün başına TOPLAM_HEDEF yorum.
# Önce 1,2,3,4 yıldızdan ÖN_HEDEF kadar çekmeye çalışır.
# Az puanlı yorum yetersizse, kalan boşluğu 5 yıldız ile doldurur.
#
# Örnek (TOPLAM=250, ÖN=50):
#   iPhone 13: 1⭐(50)+2⭐(50)+3⭐(50)+4⭐(50)+5⭐(50) = 250 ✓
#   AirPods az: 1⭐(20)+2⭐(15)+3⭐(30)+4⭐(45)+5⭐(140) = 250 ✓
TOPLAM_HEDEF        = 250  # Ürün başına toplam yorum
ON_HEDEF_PER_PUAN   = 50   # 1,2,3,4 yıldız için ön hedef (mümkünse bu kadar)
                            # 5 yıldız → kalan kotayı doldurur
PUAN_SIRASI         = [1, 2, 3, 4, 5]  # Sıra önemli: önce düşük, sona 5

SAYFA_BEKLEME       = 6
DROPDOWN_BEKLEME    = 2
FILTRE_BEKLEME      = 4   # Uygula tıkladıktan sonra
URUN_ARASI_BEKLEME  = 4
CIKTI_DOSYASI       = "trendyol_yorumlar_dengeli.csv"


# ─────────────────────────────────────────────
# ASPECT + SENTIMENT
# ─────────────────────────────────────────────

ASPECT_SOZLUGU = {
    "KARGO":   ["kargo", "teslimat", "teslim", "kurye", "gönderim", "ulaştı", "geldi", "hızlı geldi", "geç geldi"],
    "KALITE":  ["kalite", "kaliteli", "sağlam", "dayanıklı", "malzeme", "bozuldu", "kırıldı", "sorunlu", "hatalı", "defolu", "orijinal", "sahte", "muadil"],
    "FIYAT":   ["fiyat", "pahalı", "ucuz", "uygun", "değer", "lira", "tl", "indirim", "kampanya", "fiyat performans"],
    "BATARYA": ["batarya", "pil", "şarj", "şarjı", "ısınma", "mah"],
    "MEDYA":   ["kamera", "ekran", "ses", "görüntü", "çözünürlük", "fotoğraf", "video", "hoparlör", "mikrofon"],
    "AMBALAJ": ["ambalaj", "kutu", "paket", "ezilmiş", "kırık geldi", "bubble"],
    "HIZMET":  ["müşteri hizmetleri", "iade", "garanti", "destek", "iletişim", "servis", "satıcı", "şikayet"],
}

POZITIF = ["harika", "mükemmel", "süper", "güzel", "iyi", "hızlı", "sağlam", "memnun", "teşekkür",
           "tavsiye", "kaliteli", "efsane", "sorunsuz", "uygun", "orijinal", "dakik", "fena değil",
           "gayet iyi", "çok iyi", "muhteşem"]

NEGATIF = ["kötü", "rezalet", "yavaş", "geç", "bozuk", "sorunlu", "memnun değil", "şikayet", "iade",
           "hatalı", "defolu", "pahalı", "hayal kırıklığı", "çalışmıyor", "kırık", "hasarlı",
           "sahte", "aldanmayın", "dikkat"]


def kelime_var_mi(metin: str, kelime: str) -> bool:
    return bool(re.search(r"\b" + re.escape(kelime) + r"\b", metin))

def aspect_tespit_et(metin: str) -> str:
    temiz = metin.lower()
    bulunan = [a for a, kl in ASPECT_SOZLUGU.items() if any(kelime_var_mi(temiz, k) for k in kl)]
    return "|".join(bulunan) if bulunan else "GENEL"

def sentiment_hesapla(metin: str) -> str:
    temiz = metin.lower()
    poz = sum(1 for k in POZITIF if kelime_var_mi(temiz, k))
    neg = sum(1 for k in NEGATIF if kelime_var_mi(temiz, k))
    if neg > poz: return "NEG"
    if poz > neg: return "POZ"
    return "NOTR"


# ─────────────────────────────────────────────
# SELENIUM KURULUM
# ─────────────────────────────────────────────

def setup_driver() -> webdriver.Chrome:
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,900")
    options.add_argument("--window-position=0,0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    )
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })
    return driver


# ─────────────────────────────────────────────
# HTML PARSE
# ─────────────────────────────────────────────

AY_MAP = {
    "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04",
    "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08",
    "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12"
}

def parse_date(el) -> str:
    if not el: return ""
    spans = el.find_all("span")
    if len(spans) >= 3:
        gun = spans[0].get_text(strip=True)
        ay  = AY_MAP.get(spans[1].get_text(strip=True), "00")
        yil = spans[2].get_text(strip=True)
        return f"{yil}-{ay}-{gun.zfill(2)}"
    return el.get_text(strip=True)

def parse_rating(card) -> int:
    """
    Yıldız puanını padding-inline-end değerinden hesaplar.
    Trendyol'un gerçek değerleri:
      5⭐: 0px
      4⭐: ~16.71px
      3⭐: ~33.43px
      2⭐: ~50.14px
      1⭐: ~66.86px
    Her yıldız ~16.71px (5 yıldızlık container ~83.57px)
    """
    full_star = card.select_one("div.star-rating-full-star")
    if full_star:
        style = full_star.get("style", "")
        m = re.search(r'padding-inline-end:\s*([\d.]+)px', style)
        if m:
            padding = float(m.group(1))
            # padding=0 → 5⭐, padding=66.86 → 1⭐
            # En yakın puanı bul (16.71px aralıklarla)
            yildiz_genisligi = 16.71
            yildiz = 5 - round(padding / yildiz_genisligi)
            return max(1, min(5, yildiz))
    return 5

def parse_sayfa(soup: BeautifulSoup) -> list[dict]:
    yorumlar = []
    review_list = soup.select_one("div.review-list")
    if not review_list:
        return yorumlar

    cards = review_list.select("div.review")

    for card in cards:
        metin = ""
        for sel in [
            "span.review-comment > span",
            "div.review-comment span",
            "div.review-comment",
        ]:
            el = card.select_one(sel)
            if el:
                metin = el.get_text(strip=True).replace("Devamını Oku", "").strip()
                if metin: break

        if not metin: continue

        user_el   = card.select_one("div.detail-item.name")
        date_el   = card.select_one("div.detail-item.date")
        seller_el = card.select_one("span.seller-name-wrapper strong")
        likes_el  = card.select_one("span.like-button-likes-count")

        likes = 0
        if likes_el:
            m = re.search(r'\((\d+)\)', likes_el.get_text(strip=True))
            likes = int(m.group(1)) if m else 0

        yorumlar.append({
            "text":      metin,
            "rating":    parse_rating(card),
            "user":      user_el.get_text(strip=True) if user_el else "",
            "date":      parse_date(date_el),
            "seller":    seller_el.get_text(strip=True) if seller_el else "",
            "likes":     likes,
            "aspects":   aspect_tespit_et(metin),
            "sentiment": sentiment_hesapla(metin),
        })

    return yorumlar


# ─────────────────────────────────────────────
# FİLTRE FONKSİYONLARI — GERÇEK SELECTORLER
# ─────────────────────────────────────────────

def cookie_kapat(driver):
    for sel in ["#onetrust-accept-btn-handler", "button.cookie-accept"]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(1)
            return
        except: pass


def puan_dropdown_ac(driver) -> bool:
    """Puan dropdown'unu açar. Açıksa zaten True döner."""
    # Zaten açık mı?
    try:
        driver.find_element(By.CSS_SELECTOR,
            "div.filter-dropdown-open[data-testid='filter-dropdown-rate']")
        return True
    except:
        pass

    # Aç
    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='filter-toggle-rate']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(DROPDOWN_BEKLEME)
        return True
    except Exception as e:
        print(f"    ✗ Puan butonu tıklanamadı: {e}")
        return False


def puan_filtresi_uygula(driver, puan: int) -> bool:
    """
    Belirli bir yıldızın checkbox'ını seçer ve "Uygula" tıklar.
    Sıra: dropdown'da 5,4,3,2,1 → index 0,1,2,3,4
    Yani puan=5 → index=0, puan=1 → index=4
    """
    print(f"    → {puan} yıldız filtresi uygulanıyor...", end=" ", flush=True)

    if not puan_dropdown_ac(driver):
        return False

    # Checkbox sıralaması: 5 (üstte) → 1 (altta)
    index = 5 - puan  # puan=5 → 0, puan=4 → 1, ..., puan=1 → 4

    try:
        # checkbox-list içindeki label'ları al
        labels = driver.find_elements(By.CSS_SELECTOR,
            "div[data-testid='filter-items-list-rate'] > label")

        if len(labels) < 5:
            print(f"✗ sadece {len(labels)} checkbox bulundu (5 olmalı)")
            return False

        target_label = labels[index]
        # İçindeki checkbox'a tıkla (label'a tıklayınca da çalışır)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target_label)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", target_label)
        time.sleep(1)

        # Uygula butonuna tıkla
        apply_btn = driver.find_element(By.CSS_SELECTOR,
            "button[data-testid='filter-apply-button-rate']")
        driver.execute_script("arguments[0].click();", apply_btn)
        time.sleep(FILTRE_BEKLEME)

        print("✓")
        return True

    except Exception as e:
        print(f"✗ hata: {e}")
        return False


# ─────────────────────────────────────────────
# YARDIMCI
# ─────────────────────────────────────────────

def scroll_yorumlari_yukle(driver, hedef: int) -> int:
    """Infinite scroll — hedef sayıya kadar veya yeni gelmeyene kadar."""
    onceki = 0
    durma_sayaci = 0

    # Başlangıçta filtreli sayfa render olsun diye biraz bekle
    time.sleep(2)

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("div.review-list div.review")
        simdi = len(cards)

        if simdi >= hedef:
            return simdi

        if simdi == onceki:
            durma_sayaci += 1
            if durma_sayaci >= 4:  # 3 yerine 4 — daha sabırlı
                return simdi
        else:
            durma_sayaci = 0

        onceki = simdi
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)


# ─────────────────────────────────────────────
# ÜRÜN BAZLI ÇEKME
# ─────────────────────────────────────────────

def _bir_puan_cek(driver, yorum_url, puan, hedef, gorulen_metinler,
                   urun_adi, urun_id) -> list[dict]:
    """Tek bir puan için filtre uygula + scroll + parse. Listeye dönüş yapar."""
    print(f"\n  ━━ {puan} YILDIZ (hedef: {hedef}) ━━")
    print(f"  → Sayfa açılıyor...", flush=True)

    # Cache'i bypass etmek için URL'ye timestamp ekle
    fresh_url = f"{yorum_url}?_={int(time.time() * 1000)}"
    driver.get(fresh_url)
    time.sleep(SAYFA_BEKLEME)
    cookie_kapat(driver)
    time.sleep(1)

    # Yorumların yüklenmesini bekle
    print(f"  → Yorum DOM yükleniyor...", end=" ", flush=True)
    yorum_yuklendi = False
    for _ in range(20):
        soup_test = BeautifulSoup(driver.page_source, "html.parser")
        if soup_test.select("div.review-list div.review"):
            yorum_yuklendi = True
            break
        time.sleep(1)
    print("✓" if yorum_yuklendi else "✗ (devam ediliyor)")

    # ÖNEMLİ: Sayfayı "uyandır" — küçük bir scroll-up + scroll-down lazy-load için
    # Puan butonu bazen sayfa hareket etmeden render edilmiyor
    driver.execute_script("window.scrollTo(0, 100);")
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    # Puan butonu görünene kadar bekle (15 saniye)
    print(f"  → Puan butonu aranıyor...", end=" ", flush=True)
    puan_button_var = False
    for sn in range(15):
        try:
            btns = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='filter-toggle-rate']")
            if btns and btns[0].is_displayed():
                puan_button_var = True
                print(f"✓ ({sn+1}sn'de bulundu)")
                break
        except:
            pass
        time.sleep(1)

    if not puan_button_var:
        print(f"✗ 15sn bekledi yine yok, atlanıyor.")
        # Debug için ekran görüntüsü kaydet
        try:
            driver.save_screenshot(f"hata_p{puan}_{urun_id}.png")
            print(f"  📸 Hata screenshot kaydedildi: hata_p{puan}_{urun_id}.png")
        except:
            pass
        return []

    # Filtreyi uygula
    if not puan_filtresi_uygula(driver, puan):
        print(f"  ✗ {puan} yıldız filtresi uygulanamadı, atlanıyor.")
        return []

    # Scroll ile yükle
    print(f"  → Scroll ile yükleniyor...", end=" ", flush=True)
    toplam = scroll_yorumlari_yukle(driver, hedef)
    print(f"{toplam} yorum yüklendi.")

    # Parse
    soup = BeautifulSoup(driver.page_source, "html.parser")
    yorumlar = parse_sayfa(soup)

    # Duplicate kontrolü + meta ekle
    bu_puana_ait = []
    rating_uyumsuz = 0
    for y in yorumlar:
        if y["text"] in gorulen_metinler:
            continue
        gorulen_metinler.add(y["text"])

        if y["rating"] != puan:
            rating_uyumsuz += 1

        y["filter_rating"] = puan
        y["product_id"]    = urun_id
        y["product_name"]  = urun_adi
        y["category"]      = KATEGORI_MAP.get(urun_id, "Diğer")

        bu_puana_ait.append(y)
        if len(bu_puana_ait) >= hedef:
            break

    if rating_uyumsuz > 0:
        print(f"  ⚠ {rating_uyumsuz} yorumun parse_rating'i {puan} ile uyuşmadı (filtre yine de doğru)")

    print(f"  ✓ {len(bu_puana_ait)} yeni yorum eklendi")
    return bu_puana_ait


def urun_cek(driver, url: str, urun_adi: str, urun_id: str) -> list[dict]:
    """
    AKILLI KOTA SİSTEMİ + RETRY:
    1. Önce 1,2,3,4 yıldızdan ON_HEDEF_PER_PUAN kadar çekmeye çalış
    2. Az puanlıdan ne kadar çekildiyse, kalan boşluğu 5 yıldız ile doldur
    3. Bir puan 0 yorum getirirse, 1 kez daha dene (rate-limit/glitch için)
    """
    base_url = url.split("?")[0].rstrip("/")
    yorum_url = base_url + "/yorumlar"

    tum_yorumlar = []
    gorulen_metinler = set()

    def cek_with_retry(puan, hedef):
        """Bir puanı çek, 0 sonuç gelirse 1 kez retry et."""
        sonuc = _bir_puan_cek(driver, yorum_url, puan, hedef,
                               gorulen_metinler, urun_adi, urun_id)
        if not sonuc:
            print(f"  🔁 {puan}⭐ başarısız oldu, 5sn bekleyip tekrar deneniyor...")
            time.sleep(5)
            sonuc = _bir_puan_cek(driver, yorum_url, puan, hedef,
                                   gorulen_metinler, urun_adi, urun_id)
        return sonuc

    # ÖNCE: 1, 2, 3, 4 yıldız (ön hedef kadar)
    for puan in [1, 2, 3, 4]:
        yorumlar = cek_with_retry(puan, ON_HEDEF_PER_PUAN)
        tum_yorumlar.extend(yorumlar)

    # SONRA: 5 yıldız (kalan kotayı doldur)
    kalan = TOPLAM_HEDEF - len(tum_yorumlar)
    if kalan > 0:
        print(f"\n  📊 Şu ana kadar {len(tum_yorumlar)} yorum. 5⭐ ile {kalan} yorum daha çekilecek.")
        yorumlar_5 = cek_with_retry(5, kalan)
        tum_yorumlar.extend(yorumlar_5)
    else:
        print(f"\n  📊 Hedef ({TOPLAM_HEDEF}) zaten doldu, 5⭐ atlanıyor.")

    return tum_yorumlar


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  TRENDYOL YORUM SCRAPER - Selenium v7.1 (Akıllı Kota)")
    print("=" * 60)
    print(f"  Ürün sayısı          : {len(URUN_LISTESI)}")
    print(f"  Toplam hedef/ürün    : {TOPLAM_HEDEF}")
    print(f"  1-4⭐ ön hedef/puan  : {ON_HEDEF_PER_PUAN}")
    print(f"  5⭐                  : kalan kotayı doldurur")
    print(f"  Hedef toplam         : ~{len(URUN_LISTESI) * TOPLAM_HEDEF}\n")

    print("[*] Chrome başlatılıyor...")
    driver = setup_driver()
    tum_yorumlar = []

    try:
        for i, url in enumerate(URUN_LISTESI, 1):
            m = re.search(r'-p-(\d+)', url)
            urun_id  = m.group(1) if m else str(i)
            parca    = url.rstrip("/").split("/")[-1]
            urun_adi = re.sub(r'-p-\d+$', '', parca).replace("-", " ").title()

            print(f"\n{'='*60}")
            print(f"[{i}/{len(URUN_LISTESI)}] {urun_adi}")
            print(f"  ID: {urun_id} | Kategori: {KATEGORI_MAP.get(urun_id, '?')}")
            print('='*60)

            try:
                yorumlar = urun_cek(driver, url, urun_adi, urun_id)
            except Exception as e:
                print(f"  ✗ Hata: {e}")
                yorumlar = []

            tum_yorumlar.extend(yorumlar)
            print(f"\n  ✅ Bu ürün toplam: {len(yorumlar)} | Genel toplam: {len(tum_yorumlar)}")

            if i < len(URUN_LISTESI):
                print(f"  ⏳ {URUN_ARASI_BEKLEME}sn bekleniyor...")
                time.sleep(URUN_ARASI_BEKLEME)

    finally:
        driver.quit()
        print("\n[*] Browser kapatıldı.")

    if not tum_yorumlar:
        print("\n✗ Hiç yorum çekilemedi.")
        return

    df = pd.DataFrame(tum_yorumlar)
    sutunlar = ["product_name", "product_id", "category",
                "text", "rating", "filter_rating", "user", "date", "seller", "likes",
                "aspects", "sentiment"]
    df = df[[s for s in sutunlar if s in df.columns]]
    df.to_csv(CIKTI_DOSYASI, index=False, encoding="utf-8-sig")

    print("\n" + "=" * 60)
    print("  ✅ TAMAMLANDI")
    print("=" * 60)
    print(f"\n  Toplam yorum : {len(df)}")
    print(f"  Ürün sayısı  : {df['product_id'].nunique()}")
    print(f"  Dosya        : {CIKTI_DOSYASI}")

    print("\n📊 Filtre puanı dağılımı (yani gerçek puan):")
    if "filter_rating" in df.columns:
        print(df["filter_rating"].value_counts().sort_index().to_string())

    print("\n📊 Parse edilen rating dağılımı:")
    print(df["rating"].value_counts().sort_index().to_string())

    print("\n📈 Ürün × puan dağılımı:")
    if "filter_rating" in df.columns:
        pivot = df.pivot_table(index="product_name", columns="filter_rating",
                               values="text", aggfunc="count", fill_value=0)
        print(pivot.to_string())

    print("\n📊 Sentiment:")
    print(df["sentiment"].value_counts().to_string())

    print("\n📊 Aspect dağılımı:")
    sayac = Counter()
    for row in df["aspects"]:
        sayac.update(row.split("|"))
    for a, s in sayac.most_common():
        print(f"  {a:12s}: {s}")


if __name__ == "__main__":
    main()
