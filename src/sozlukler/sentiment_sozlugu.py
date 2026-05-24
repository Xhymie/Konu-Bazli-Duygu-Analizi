# -*- coding: utf-8 -*-
"""
Sentiment Sözlükleri
====================
Pozitif ve negatif kelime/ifade listeleri.
Kategoriler: güçlü, orta, zayıf, fiil, argo, beklenti, arıza, aldatılma.
"""

# ============================================================================
# POZİTİF KELİMELER (70+ kelime/ifade)
# ============================================================================

POZITIF_KELIMELER = [
    # --- Güçlü pozitif ---
    "mükemmel", "harika", "muhteşem", "olağanüstü", "kusursuz",
    "fevkalade", "enfes", "şahane", "mükemmell", "harikaydı",
    # --- Orta pozitif ---
    "iyi", "güzel", "başarılı", "kaliteli", "düzgün", "sağlam",
    "hoş", "tatmin edici", "yeterli", "gayet iyi", "bayıldım",
    # --- Zayıf pozitif ---
    "fena değil", "idare eder", "makul", "ortalama üstü",
    "kabul edilebilir", "yeterince iyi", "kötü sayılmaz",
    "eh işte", "şöyle böyle iyi",
    # --- Fiil formları ---
    "beğendim", "memnun kaldım", "tavsiye ederim", "öneririm",
    "sevdim", "aldığıma sevindim", "memnunum", "mutluyum",
    "hayran kaldım", "çok sevdim", "etkilendim", "şaşırdım",
    "beklentimi karşıladı", "beklediğimden iyi",
    # --- Argo / samimi ---
    "süper", "efsane", "çok iyi", "tam istediğim", "bomba gibi",
    "canavar gibi", "üstüne yok", "on numara", "10 numara",
    "5 yıldız", "beş yıldız", "helal olsun", "bravo",
    "oha", "vay be", "eline sağlık",
    # --- Beklenti karşılama ---
    "beklediğim gibi", "pişman değilim", "değdi",
    "parasının karşılığı", "hak ediyor", "tam olması gerektiği gibi",
    "her kuruşuna değer", "tekrar alırım",
    # --- Hız / performans pozitif ---
    "hızlı", "akıcı", "pürüzsüz", "stabil", "sorunsuz",
    "hızlıydı", "zamanında",
]

# ============================================================================
# NEGATİF KELİMELER (70+ kelime/ifade)
# ============================================================================

NEGATIF_KELIMELER = [
    # --- Güçlü negatif ---
    "berbat", "rezalet", "korkunç", "iğrenç", "felaket", "facia",
    "rezil", "skandal", "vahim", "işkence",
    # --- Orta negatif ---
    "kötü", "bozuk", "yetersiz", "hayal kırıklığı", "vasat",
    "zayıf", "düşük", "başarısız", "sorunlu", "problemli",
    "eksik", "hatalı", "sıkıntılı",
    # --- Zayıf negatif ---
    "pek iyi değil", "biraz sorunlu", "biraz kötü",
    "çok da iyi değil", "beklentimin altında",
    # --- Fiil formları ---
    "beğenmedim", "pişman oldum", "iade ettim", "iade edeceğim",
    "şikayet ettim", "geri gönderdim", "razı değilim",
    "memnun değilim", "memnun kalmadım", "hoşlanmadım",
    # --- Arıza ifadeleri ---
    "çalışmıyor", "bozuldu", "kırıldı", "donuyor", "kasıyor",
    "takılıyor", "kapanıyor", "açılmıyor", "yanıt vermiyor",
    "hata veriyor", "çöküyor", "yavaşlıyor", "ısınıyor",
    "arızalı", "defolu", "patladı", "söndü",
    # --- Argo / samimi ---
    "çöp", "bok gibi", "atmak lazım", "leş", "dandik",
    "yok artık", "saçmalık", "zırva", "boş",
    # --- Aldatılma hissi ---
    "dolandırıcılık", "sahte", "yanıltıcı", "fotoğraftaki gibi değil",
    "dolandırıldım", "kandırıldım", "kopya", "taklit",
    "reklam gibi değil", "açıklamayla uyuşmuyor",
    # --- Diğer negatif ---
    "pahalı", "geç", "yavaş", "ağır", "kırılgan",
    "pişmanım", "üzgünüm",
]
