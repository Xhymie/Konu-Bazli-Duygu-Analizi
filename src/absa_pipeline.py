# -*- coding: utf-8 -*-
"""
Kural Tabanli Aspect-Based Sentiment Analysis (ABSA) Pipeline
===============================================================
Trendyol teknoloji urunu yorumlarindan 7 aspect icin sentiment cikarir.
Aspectler: kargo, kalite, fiyat, batarya, ses_goruntu, ambalaj, genel

Kullanim:
    from absa_pipeline import absa_pipeline
    sonuclar = absa_pipeline("Kargo cok hizli geldi ama batarya kotu.")
"""

import re

from sozlukler import (
    ASPECT_SOZLUGU,
    POZITIF_KELIMELER,
    NEGATIF_KELIMELER,
    OLUMSUZLAMA_KALIPLARI,
    BAGLACLAR,
)
from on_isleme import on_isleme


# ============================================================================
# CÜMLE BÖLME
# ============================================================================

def cumlelere_bol(metin):
    """
    Yorumu cumlelere boler.

    Bolme kriterleri:
    1. Noktalama isaretleri: . ! ?
    2. Karsitlik baglaclari: ama, fakat, ancak, lakin, bununla birlikte,
       ne var ki, yalniz

    Args:
        metin (str): On islemeden gecmis yorum metni

    Returns:
        list: Cumle listesi (bos cumleler filtrelenmis)
    """
    metin = metin.strip()
    if not metin:
        return []

    # 1. Noktalama isaretlerinden bol
    parcalar = re.split(r'[.!?]+', metin)

    # 2. Her parcayi baglaclardan bol
    cumleler = []
    for parca in parcalar:
        baglac_pattern = r'\b(?:' + '|'.join(BAGLACLAR) + r')\b'
        alt_parcalar = re.split(baglac_pattern, parca, flags=re.IGNORECASE)
        for alt in alt_parcalar:
            temiz = alt.strip()
            if temiz:
                cumleler.append(temiz)

    return cumleler


# ============================================================================
# ASPECT TESPİTİ
# ============================================================================

def cumledeki_aspectler(cumle):
    """
    Bir cumlede hangi aspectlerin gectigini tespit eder.

    Hem tam kelime hem alt-dize eslesmesi yapilir:
    - "batarya" -> "batarya", "bataryasi", "bataryam" icin eslesir
    - Bilesik ifadeler de kontrol edilir

    Args:
        cumle (str): Tek bir cumle metni (on islemeden gecmis)

    Returns:
        list: Bulunan aspect isimlerinin listesi (or. ["kargo", "batarya"])
    """
    cumle_lower = cumle.lower()
    bulunan_aspectler = []

    for aspect, kelimeler in ASPECT_SOZLUGU.items():
        if aspect == "genel":
            continue  # Genel aspekti ozel olarak ele alacagiz
        for kelime in kelimeler:
            if kelime.lower() in cumle_lower:
                bulunan_aspectler.append(aspect)
                break

    return bulunan_aspectler


# ============================================================================
# OLUMSUZLAMA TESPİTİ
# ============================================================================

def _olumsuzlama_var_mi(cumle):
    """
    Cumlede olumsuzlama olup olmadigini kontrol eder.

    Cumle bazinda calisir. Olumsuzlama kaliplarindan herhangi biri
    cumlede geciyorsa True doner.

    Args:
        cumle (str): Tek bir cumle metni

    Returns:
        bool: Olumsuzlama varsa True
    """
    cumle_lower = cumle.lower()
    for kalip in OLUMSUZLAMA_KALIPLARI:
        if kalip in cumle_lower:
            return True
    return False


# ============================================================================
# SENTIMENT HESAPLAMA
# ============================================================================

def sentiment_hesapla(cumle):
    """
    Bir cumlenin sentiment etiketini ve guven skorunu hesaplar.

    Gelismis Algoritma:
    1. Once "pozitif_kelime + degil/yok" kaliplarini tespit et
       -> Bu kaliptaki pozitif kelimeyi say, negatif olarak degerlendir
    2. Once "negatif_kelime + degil/yok" kaliplarini tespit et
       -> Bu kaliptaki negatif kelimeyi say, pozitif olarak degerlendir
    3. Kalan (olumsuzlanmamis) pozitif ve negatif kelimeleri say
    4. Skor = |pozitif_sayi - negatif_sayi|

    Args:
        cumle (str): Tek bir cumle metni (on islemeden gecmis)

    Returns:
        tuple: (etiket, skor) -> etiket: "pozitif"/"negatif"/"notr", skor: int
    """
    cumle_lower = cumle.lower()

    pozitif_sayi = 0
    negatif_sayi = 0

    # Olumsuzlama ekleri (kelimeden hemen sonra gelebilecek)
    olumsuzlama_sonekleri = ["degil", "degildi", "degilim",
                             "değil", "değildi", "değilim",
                             "yok", "yoktu"]

    # --- 1. "pozitif + degil" kaliplari -> negatif say ---
    olumsuzlanmis_pozitifler = set()
    for kelime in POZITIF_KELIMELER:
        k = kelime.lower()
        if k in cumle_lower:
            for son_ek in olumsuzlama_sonekleri:
                kalip = k + " " + son_ek
                if kalip in cumle_lower:
                    negatif_sayi += 1
                    olumsuzlanmis_pozitifler.add(k)
                    break

    # --- 2. "negatif + degil" kaliplari -> pozitif say ---
    olumsuzlanmis_negatifler = set()
    for kelime in NEGATIF_KELIMELER:
        k = kelime.lower()
        if k in cumle_lower:
            for son_ek in olumsuzlama_sonekleri:
                kalip = k + " " + son_ek
                if kalip in cumle_lower:
                    pozitif_sayi += 1
                    olumsuzlanmis_negatifler.add(k)
                    break

    # --- 3. Olumsuzlanmamis pozitif kelimeleri say ---
    for kelime in POZITIF_KELIMELER:
        k = kelime.lower()
        if k in cumle_lower and k not in olumsuzlanmis_pozitifler:
            pozitif_sayi += 1

    # --- 4. Olumsuzlanmamis negatif kelimeleri say ---
    for kelime in NEGATIF_KELIMELER:
        k = kelime.lower()
        if k in cumle_lower and k not in olumsuzlanmis_negatifler:
            negatif_sayi += 1

    # --- 5. Sentiment belirle ---
    if pozitif_sayi > negatif_sayi:
        sentiment = "pozitif"
    elif negatif_sayi > pozitif_sayi:
        sentiment = "negatif"
    else:
        if _olumsuzlama_var_mi(cumle):
            sentiment = "negatif"
        else:
            sentiment = "notr"

    skor = abs(pozitif_sayi - negatif_sayi)
    return (sentiment, skor)


# ============================================================================
# ANA PIPELINE
# ============================================================================

def absa_pipeline(yorum_metni):
    """
    Ana ABSA pipeline fonksiyonu.

    Bir yorum metnini alir ve [(aspect, sentiment, cumle, skor), ...] doner.

    Is akisi:
    1. On isleme uygula (kucuk harf, temizleme, normalizasyon)
    2. Yorum -> cumlelere bolunur
    3. Her cumle -> aspect tespiti
    4. Aspect bulunan cumle -> sentiment hesaplama
    5. Hicbir cumlede aspect bulunamazsa -> "genel" aspekti atanir
    6. Bir cumlede birden fazla aspect varsa her biri ayri kayit olur

    Args:
        yorum_metni (str): Ham yorum metni

    Returns:
        list of tuple: [(aspect, sentiment, cumle, skor), ...]
    """
    # --- On isleme ---
    temiz_metin = on_isleme(yorum_metni)

    cumleler = cumlelere_bol(temiz_metin)
    sonuclar = []
    herhangi_aspect_bulundu = False

    for cumle in cumleler:
        aspectler = cumledeki_aspectler(cumle)

        if aspectler:
            herhangi_aspect_bulundu = True
            sentiment, skor = sentiment_hesapla(cumle)
            for asp in aspectler:
                sonuclar.append((asp, sentiment, cumle, skor))
        else:
            # "genel" aspect kelimesi var mi kontrol et
            cumle_lower = cumle.lower()
            genel_bulundu = False
            for kelime in ASPECT_SOZLUGU["genel"]:
                if kelime.lower() in cumle_lower:
                    genel_bulundu = True
                    break
            if genel_bulundu:
                herhangi_aspect_bulundu = True
                sentiment, skor = sentiment_hesapla(cumle)
                sonuclar.append(("genel", sentiment, cumle, skor))

    # Hic aspect bulunamadiysa tum yorumu "genel" olarak degerlendir
    if not herhangi_aspect_bulundu:
        sentiment, skor = sentiment_hesapla(temiz_metin)
        sonuclar.append(("genel", sentiment, temiz_metin, skor))

    return sonuclar
