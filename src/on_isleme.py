# -*- coding: utf-8 -*-
"""
Metin Ön İşleme Modülü
========================
Trendyol yorumlarına sentiment analizi öncesi uygulanan temizleme adımları.

Pipeline sırası:
    1. Küçük harfe çevir
    2. URL'leri kaldır
    3. Emoji'leri kaldır
    4. Tekrarlı karakterleri normalize et (çoooook → çok)
    5. Özel karakterleri temizle (noktalama hariç)
    6. Fazla boşlukları temizle
"""

import re


def kucuk_harfe_cevir(metin):
    """
    Metni Türkçe uyumlu küçük harfe çevirir.

    Python'un lower() metodu Türkçe İ→i, I→ı dönüşümünü düzgün yapmaz.
    Bu fonksiyon önce Türkçe büyük harfleri elle dönüştürür.

    Args:
        metin (str): Ham metin

    Returns:
        str: Küçük harfe çevrilmiş metin
    """
    # Türkçe özel karakter dönüşümleri
    metin = metin.replace("İ", "i").replace("I", "ı")
    return metin.lower()


def url_temizle(metin):
    """
    Metindeki URL'leri kaldırır.

    http://, https://, www. ile başlayan linkleri temizler.

    Args:
        metin (str): Metin

    Returns:
        str: URL'lerden arındırılmış metin
    """
    return re.sub(r'https?://\S+|www\.\S+', '', metin)


def emoji_temizle(metin):
    """
    Metindeki emoji ve özel Unicode karakterlerini kaldırır.

    Trendyol yorumlarında sıkça kullanılan emoji'ler sentiment
    analizini bozabilir (sözlük tabanlı sistemde).

    Args:
        metin (str): Metin

    Returns:
        str: Emoji'lerden arındırılmış metin
    """
    # Geniş emoji Unicode aralıkları
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # Yüz ifadeleri
        "\U0001F300-\U0001F5FF"  # Semboller & piktogramlar
        "\U0001F680-\U0001F6FF"  # Ulaşım & harita
        "\U0001F1E0-\U0001F1FF"  # Bayraklar
        "\U00002702-\U000027B0"  # Dingbats
        "\U000024C2-\U0001F251"  # Çeşitli semboller
        "\U0001F900-\U0001F9FF"  # Ek yüz ifadeleri
        "\U0001FA00-\U0001FA6F"  # Satranç, vb.
        "\U0001FA70-\U0001FAFF"  # Ek semboller
        "\U00002600-\U000026FF"  # Çeşitli semboller
        "\U0000FE00-\U0000FE0F"  # Varyasyon seçiciler
        "\U0000200D"             # Zero-width joiner
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub('', metin)


def tekrarli_karakter_normalize(metin):
    """
    Ardışık tekrarlı karakterleri normalize eder.

    Trendyol kullanıcıları vurgu için karakter tekrarı yapar:
        "çoooook güzeeeel" → "çook güzeel"
        "harikaaaa" → "harikaa"

    3+ tekrar → 2'ye düşürülür (Türkçede bazı çift harfler olabilir).

    Args:
        metin (str): Metin

    Returns:
        str: Normalize edilmiş metin
    """
    return re.sub(r'(.)\1{2,}', r'\1\1', metin)


def ozel_karakter_temizle(metin):
    """
    Anlamsız özel karakterleri kaldırır.

    Noktalama işaretleri (. ! ? ,) korunur çünkü cümle bölmede lazım.
    Türkçe karakterler (ş, ğ, ü, ö, ç, ı) korunur.

    Args:
        metin (str): Metin

    Returns:
        str: Temizlenmiş metin
    """
    # Sadece harf, rakam, boşluk ve temel noktalama bırak
    return re.sub(r'[^\w\s.!?,;:\'-]', ' ', metin)


def fazla_bosluk_temizle(metin):
    """
    Ardışık boşlukları tek boşluğa düşürür ve baş/son boşlukları kaldırır.

    Args:
        metin (str): Metin

    Returns:
        str: Temizlenmiş metin
    """
    return re.sub(r'\s+', ' ', metin).strip()


def on_isleme(metin):
    """
    Tüm ön işleme adımlarını sırayla uygulayan ana fonksiyon.

    Pipeline:
        Ham metin
        → küçük harf
        → URL temizle
        → emoji temizle
        → tekrarlı karakter normalize
        → özel karakter temizle
        → fazla boşluk temizle
        → Temiz metin

    Args:
        metin (str): Ham yorum metni

    Returns:
        str: Ön işlemeden geçmiş temiz metin
    """
    if not metin or not isinstance(metin, str):
        return ""

    metin = kucuk_harfe_cevir(metin)
    metin = url_temizle(metin)
    metin = emoji_temizle(metin)
    metin = tekrarli_karakter_normalize(metin)
    metin = ozel_karakter_temizle(metin)
    metin = fazla_bosluk_temizle(metin)

    return metin
