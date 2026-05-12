"""
Trendyol yorum toplama betiği.

Selenium ile ürün sayfasındaki "Puan" filtresini sırayla uygulayıp her yıldız
seviyesinden (1..5) yorum çeker. Düşük puanlı yorumlar ön kotayla, kalan kotayı
5 yıldız yorumlarla doldurur. Toplanan veriler CSV'ye yazılır.

Çalıştırma:
    python src/scrape_trendyol.py
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


# Ürün listesi ve kategori eşlemesi
URUN_LISTESI = [
    "https://www.trendyol.com/apple/iphone-13-128-gb-yildiz-isigi-cep-telefonu-apple-turkiye-garantili-p-150059024",
    "https://www.trendyol.com/apple/iphone-11-128-gb-beyaz-cep-telefonu-aksesuarsiz-kutu-apple-turkiye-garantili-p-64074794",
    "https://www.trendyol.com/apple/airpods-2-nesil-kulaklik-p-6405631",
    "https://www.trendyol.com/apple/airpods-4-nesil-mxp63tu-a-p-857508954",
    "https://www.trendyol.com/apple/macbook-air-m1-cip-8gb-256gb-ssd-macos-13-qhd-tasinabilir-bilgisayar-uzay-grisi-p-68042136",
    "https://www.trendyol.com/lenovo/ideapad-slim-3-intel-n100-4gb-ram-128gb-ssd-15-6-p-1057359906",
    "https://www.trendyol.com/xiaomi/redmi-buds-6-play-siyah-kulakici-kulaklik-gurultu-onleme-bt5-4-ios-android-xiaomi-tr-garantili-p-855229295",
    "https://www.trendyol.com/casper/nirvana-intel-celeron-n4020-4gb-ram-120gb-ssd-windows-11-home-15-6-hd-laptop-c370-4020-4c00b-p-358003688",
    "https://www.trendyol.com/samsung/galaxy-a24-128-gb-siyah-cep-telefonu-samsung-turkiye-garantili-p-700100969",
]

KATEGORI_MAP = {
    "150059024":  "Telefon",
    "64074794":   "Telefon",
    "6405631":    "Kulaklık",
    "857508954":  "Kulaklık",
    "855229295":  "Kulaklık",
    "68042136":   "Bilgisayar",
    "1057359906": "Bilgisayar",
    "358003688":  "Bilgisayar",
    "700100969":  "Telefon",
}

# Kota ayarları: ürün başına hedeflenen toplam yorum sayısı ve düşük puanlı
# yorumlar için ön hedef. 5 yıldız kalan kotayı doldurur.
TOPLAM_HEDEF        = 250
ON_HEDEF_PER_PUAN   = 50
PUAN_SIRASI         = [1, 2, 3, 4, 5]

SAYFA_BEKLEME       = 6
DROPDOWN_BEKLEME    = 2
FILTRE_BEKLEME      = 4
URUN_ARASI_BEKLEME  = 4

# None ise URUN_LISTESI'ndeki tüm ürünler çekilir, aksi halde sadece
# verilen product_id için ayrı bir dosya üretilir.
TEK_URUN_ID = "700100969"

# None | "yeni-eski" | "eski-yeni"
SIRALAMA_TIPI = "yeni-eski"

if TEK_URUN_ID:
    CIKTI_DOSYASI = f"trendyol_yorumlar_ek_{TEK_URUN_ID}.csv"
else:
    CIKTI_DOSYASI = "trendyol_yorumlar_dengeli.csv"


# Aspect (konu) sözlüğü ve basit sentiment kelime listeleri
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
    if neg > poz:
        return "NEG"
    if poz > neg:
        return "POZ"
    return "NOTR"


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


AY_MAP = {
    "Ocak": "01", "Şubat": "02", "Mart": "03", "Nisan": "04",
    "Mayıs": "05", "Haziran": "06", "Temmuz": "07", "Ağustos": "08",
    "Eylül": "09", "Ekim": "10", "Kasım": "11", "Aralık": "12",
}


def parse_date(el) -> str:
    if not el:
        return ""
    spans = el.find_all("span")
    if len(spans) >= 3:
        gun = spans[0].get_text(strip=True)
        ay  = AY_MAP.get(spans[1].get_text(strip=True), "00")
        yil = spans[2].get_text(strip=True)
        return f"{yil}-{ay}-{gun.zfill(2)}"
    return el.get_text(strip=True)


def parse_rating(card) -> int:
    # Yıldız puanı, dolu yıldız div'inin padding-inline-end stilinden
    # hesaplanır. Her yıldız ~16.71px genişliğinde, 5 yıldız 0px padding'e
    # karşılık gelir.
    full_star = card.select_one("div.star-rating-full-star")
    if full_star:
        style = full_star.get("style", "")
        m = re.search(r'padding-inline-end:\s*([\d.]+)px', style)
        if m:
            padding = float(m.group(1))
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
                if metin:
                    break

        if not metin:
            continue

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


def cookie_kapat(driver):
    for sel in ["#onetrust-accept-btn-handler", "button.cookie-accept"]:
        try:
            driver.find_element(By.CSS_SELECTOR, sel).click()
            time.sleep(1)
            return
        except Exception:
            pass


def puan_dropdown_ac(driver) -> bool:
    try:
        driver.find_element(
            By.CSS_SELECTOR,
            "div.filter-dropdown-open[data-testid='filter-dropdown-rate']",
        )
        return True
    except Exception:
        pass

    try:
        btn = driver.find_element(By.CSS_SELECTOR, "button[data-testid='filter-toggle-rate']")
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", btn)
        time.sleep(DROPDOWN_BEKLEME)
        return True
    except Exception as e:
        print(f"    Puan butonu tıklanamadı: {e}")
        return False


def puan_filtresi_uygula(driver, puan: int) -> bool:
    # Checkbox sırası dropdown'da 5..1 olduğundan puan -> index dönüşümü 5-puan.
    print(f"    -> {puan} yildiz filtresi uygulaniyor...", end=" ", flush=True)

    if not puan_dropdown_ac(driver):
        return False

    index = 5 - puan

    try:
        labels = driver.find_elements(
            By.CSS_SELECTOR,
            "div[data-testid='filter-items-list-rate'] > label",
        )

        if len(labels) < 5:
            print(f"basarisiz - sadece {len(labels)} checkbox bulundu")
            return False

        target_label = labels[index]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", target_label)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", target_label)
        time.sleep(1)

        apply_btn = driver.find_element(
            By.CSS_SELECTOR,
            "button[data-testid='filter-apply-button-rate']",
        )
        driver.execute_script("arguments[0].click();", apply_btn)
        time.sleep(FILTRE_BEKLEME)

        print("tamam")
        return True

    except Exception as e:
        print(f"hata: {e}")
        return False


# Sıralama dropdown'unda görülebilen metin varyantları.
SIRALAMA_TEXT_MAP = {
    "yeni-eski": ["Yeniden Eskiye", "En Yeni", "Yeni → Eski"],
    "eski-yeni": ["Eskiden Yeniye", "En Eski", "Eski → Yeni"],
}


def siralama_uygula(driver, tip: str) -> bool:
    # Sıralama butonunu data-testid ve metin tabanlı fallback ile arar.
    # Bulunamazsa varsayılan ("Önerilen") sıralamayla devam edilir.
    if not tip or tip not in SIRALAMA_TEXT_MAP:
        return False

    print(f"  -> Siralama '{tip}' uygulaniyor...", end=" ", flush=True)

    dropdown_btn = None
    css_kandidatlari = [
        "button[data-testid='sorting-button']",
        "button[data-testid='sort-toggle']",
        "button[data-testid='filter-toggle-sort']",
        "button[data-testid*='sort']",
        "div[data-testid*='sort'] button",
    ]
    for sel in css_kandidatlari:
        try:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed():
                    dropdown_btn = el
                    break
            if dropdown_btn:
                break
        except Exception:
            pass

    if not dropdown_btn:
        try:
            xpath = (
                "//button[contains(., 'Sırala')] | "
                "//div[contains(@class,'sort')]//button | "
                "//*[contains(text(),'Önerilen Sıralama')]/ancestor::button[1]"
            )
            for el in driver.find_elements(By.XPATH, xpath):
                if el.is_displayed():
                    dropdown_btn = el
                    break
        except Exception:
            pass

    if not dropdown_btn:
        print("siralama butonu bulunamadi, atlaniyor")
        return False

    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dropdown_btn)
        time.sleep(0.4)
        driver.execute_script("arguments[0].click();", dropdown_btn)
        time.sleep(DROPDOWN_BEKLEME)
    except Exception as e:
        print(f"dropdown acilamadi ({e}), atlaniyor")
        return False

    hedef_metinler = SIRALAMA_TEXT_MAP[tip]
    tiklandi = False
    for txt in hedef_metinler:
        try:
            xp = f"//*[normalize-space(text())='{txt}'] | //*[contains(normalize-space(text()),'{txt}')]"
            for opt in driver.find_elements(By.XPATH, xp):
                if opt.is_displayed():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", opt)
                    time.sleep(0.3)
                    driver.execute_script("arguments[0].click();", opt)
                    tiklandi = True
                    break
            if tiklandi:
                break
        except Exception:
            pass

    if not tiklandi:
        print(f"'{tip}' opsiyonu bulunamadi, atlaniyor")
        try:
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        except Exception:
            pass
        return False

    time.sleep(FILTRE_BEKLEME)
    print("tamam")
    return True


def scroll_yorumlari_yukle(driver, hedef: int) -> int:
    # Hedefe ulaşana veya yeni yorum gelmemeye başlayana kadar sayfayı kaydır.
    onceki = 0
    durma_sayaci = 0

    time.sleep(2)

    while True:
        soup = BeautifulSoup(driver.page_source, "html.parser")
        cards = soup.select("div.review-list div.review")
        simdi = len(cards)

        if simdi >= hedef:
            return simdi

        if simdi == onceki:
            durma_sayaci += 1
            if durma_sayaci >= 4:
                return simdi
        else:
            durma_sayaci = 0

        onceki = simdi
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.5)


def _bir_puan_cek(driver, yorum_url, puan, hedef, gorulen_metinler,
                  urun_adi, urun_id) -> list[dict]:
    print(f"\n  -- {puan} yildiz (hedef: {hedef}) --")

    # Cache'i bypass etmek için URL'ye timestamp ekleniyor.
    fresh_url = f"{yorum_url}?_={int(time.time() * 1000)}"
    driver.get(fresh_url)
    time.sleep(SAYFA_BEKLEME)
    cookie_kapat(driver)
    time.sleep(1)

    yorum_yuklendi = False
    for _ in range(20):
        soup_test = BeautifulSoup(driver.page_source, "html.parser")
        if soup_test.select("div.review-list div.review"):
            yorum_yuklendi = True
            break
        time.sleep(1)
    if not yorum_yuklendi:
        print("  Yorum DOM yuklenemedi, yine de devam ediliyor.")

    # Puan butonu lazy-load oluyor; küçük bir scroll ile tetikleniyor.
    driver.execute_script("window.scrollTo(0, 100);")
    time.sleep(0.5)
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)

    # Sıralama her sayfa yüklemesinde varsayılana dönüyor, bu yüzden burada
    # tekrar uygulanıyor.
    if SIRALAMA_TIPI:
        siralama_uygula(driver, SIRALAMA_TIPI)

    puan_button_var = False
    for sn in range(15):
        try:
            btns = driver.find_elements(By.CSS_SELECTOR, "button[data-testid='filter-toggle-rate']")
            if btns and btns[0].is_displayed():
                puan_button_var = True
                break
        except Exception:
            pass
        time.sleep(1)

    if not puan_button_var:
        print("  Puan butonu bulunamadi, atlaniyor.")
        try:
            driver.save_screenshot(f"hata_p{puan}_{urun_id}.png")
        except Exception:
            pass
        return []

    if not puan_filtresi_uygula(driver, puan):
        print(f"  {puan} yildiz filtresi uygulanamadi, atlaniyor.")
        return []

    toplam = scroll_yorumlari_yukle(driver, hedef)
    print(f"  Scroll sonrasi {toplam} yorum yuklendi.")

    soup = BeautifulSoup(driver.page_source, "html.parser")
    yorumlar = parse_sayfa(soup)

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
        print(f"  Uyari: {rating_uyumsuz} yorumun parse_rating'i {puan} ile uyusmadi.")

    print(f"  {len(bu_puana_ait)} yeni yorum eklendi.")
    return bu_puana_ait


def urun_cek(driver, url: str, urun_adi: str, urun_id: str) -> list[dict]:
    # 1..4 yıldız için ön kota uygulanır, 5 yıldız kalan boşluğu doldurur.
    # Bir puan sıfır yorum getirirse aynı puan bir kez daha denenir.
    base_url = url.split("?")[0].rstrip("/")
    yorum_url = base_url + "/yorumlar"

    tum_yorumlar = []
    gorulen_metinler = set()

    def cek_with_retry(puan, hedef):
        sonuc = _bir_puan_cek(driver, yorum_url, puan, hedef,
                              gorulen_metinler, urun_adi, urun_id)
        if not sonuc:
            print(f"  {puan} yildiz icin yeniden deneniyor...")
            time.sleep(5)
            sonuc = _bir_puan_cek(driver, yorum_url, puan, hedef,
                                  gorulen_metinler, urun_adi, urun_id)
        return sonuc

    for puan in [1, 2, 3, 4]:
        yorumlar = cek_with_retry(puan, ON_HEDEF_PER_PUAN)
        tum_yorumlar.extend(yorumlar)

    kalan = TOPLAM_HEDEF - len(tum_yorumlar)
    if kalan > 0:
        print(f"\n  Su ana kadar {len(tum_yorumlar)} yorum. 5 yildizdan {kalan} yorum daha cekilecek.")
        yorumlar_5 = cek_with_retry(5, kalan)
        tum_yorumlar.extend(yorumlar_5)
    else:
        print(f"\n  Hedef ({TOPLAM_HEDEF}) doldu, 5 yildiz atlaniyor.")

    return tum_yorumlar


def main():
    if TEK_URUN_ID:
        cekilecekler = [u for u in URUN_LISTESI if f"-p-{TEK_URUN_ID}" in u]
        if not cekilecekler:
            print(f"TEK_URUN_ID='{TEK_URUN_ID}' URUN_LISTESI icinde bulunamadi.")
            return
    else:
        cekilecekler = URUN_LISTESI

    print("Trendyol Yorum Scraper")
    if TEK_URUN_ID:
        print(f"  Tek urun modu       : {TEK_URUN_ID}")
        print(f"  Cikti dosyasi       : {CIKTI_DOSYASI}")
    print(f"  Siralama tipi       : {SIRALAMA_TIPI or 'varsayilan'}")
    print(f"  Urun sayisi         : {len(cekilecekler)}")
    print(f"  Toplam hedef/urun   : {TOPLAM_HEDEF}")
    print(f"  1-4 yildiz on hedef : {ON_HEDEF_PER_PUAN}")
    print(f"  Hedef toplam        : ~{len(cekilecekler) * TOPLAM_HEDEF}\n")

    print("[*] Chrome baslatiliyor...")
    driver = setup_driver()
    tum_yorumlar = []

    try:
        for i, url in enumerate(cekilecekler, 1):
            m = re.search(r'-p-(\d+)', url)
            urun_id  = m.group(1) if m else str(i)
            parca    = url.rstrip("/").split("/")[-1]
            urun_adi = re.sub(r'-p-\d+$', '', parca).replace("-", " ").title()

            print(f"\n[{i}/{len(cekilecekler)}] {urun_adi}")
            print(f"  ID: {urun_id} | Kategori: {KATEGORI_MAP.get(urun_id, '?')}")

            try:
                yorumlar = urun_cek(driver, url, urun_adi, urun_id)
            except Exception as e:
                print(f"  Hata: {e}")
                yorumlar = []

            tum_yorumlar.extend(yorumlar)
            print(f"\n  Bu urun toplam: {len(yorumlar)} | Genel toplam: {len(tum_yorumlar)}")

            if i < len(cekilecekler):
                print(f"  {URUN_ARASI_BEKLEME} sn bekleniyor...")
                time.sleep(URUN_ARASI_BEKLEME)

    finally:
        driver.quit()
        print("\n[*] Browser kapatildi.")

    if not tum_yorumlar:
        print("\nHic yorum cekilemedi.")
        return

    df = pd.DataFrame(tum_yorumlar)
    sutunlar = ["product_name", "product_id", "category",
                "text", "rating", "filter_rating", "user", "date", "seller", "likes",
                "aspects", "sentiment"]
    df = df[[s for s in sutunlar if s in df.columns]]
    df.to_csv(CIKTI_DOSYASI, index=False, encoding="utf-8-sig")

    print("\nTamamlandi.")
    print(f"  Toplam yorum : {len(df)}")
    print(f"  Urun sayisi  : {df['product_id'].nunique()}")
    print(f"  Dosya        : {CIKTI_DOSYASI}")

    print("\nFiltre puani dagilimi:")
    if "filter_rating" in df.columns:
        print(df["filter_rating"].value_counts().sort_index().to_string())

    print("\nParse edilen rating dagilimi:")
    print(df["rating"].value_counts().sort_index().to_string())

    print("\nUrun x puan dagilimi:")
    if "filter_rating" in df.columns:
        pivot = df.pivot_table(index="product_name", columns="filter_rating",
                               values="text", aggfunc="count", fill_value=0)
        print(pivot.to_string())

    print("\nSentiment dagilimi:")
    print(df["sentiment"].value_counts().to_string())

    print("\nAspect dagilimi:")
    sayac = Counter()
    for row in df["aspects"]:
        sayac.update(row.split("|"))
    for a, s in sayac.most_common():
        print(f"  {a:12s}: {s}")


if __name__ == "__main__":
    main()
