
"""
Sentiment Sözlükleri
====================
Pozitif ve negatif kelime/ifade listeleri.
Kategoriler: güçlü, orta, zayıf, fiil, argo, beklenti, arıza, aldatılma.
"""

# ============================================================================
# POZİTİF KELİMELER 
# ============================================================================

POZITIF_KELIMELER = [
    
    "mükemmel", "harika", "muhteşem", "olağanüstü", "kusursuz",
    "fevkalade", "enfes", "şahane", "mükemmell", "harikaydı",
    
    "iyi", "güzel", "başarılı", "kaliteli", "düzgün", "sağlam",
    "hoş", "tatmin edici", "yeterli", "gayet iyi", "bayıldım",
    
    "fena değil", "idare eder", "makul", "ortalama üstü",
    "kabul edilebilir", "yeterince iyi", "kötü sayılmaz",
    "eh işte", "şöyle böyle iyi",
    
    "beğendim", "memnun kaldım", "tavsiye ederim", "öneririm",
    "sevdim", "aldığıma sevindim", "memnunum", "mutluyum",
    "hayran kaldım", "çok sevdim", "etkilendim", "şaşırdım",
    "beklentimi karşıladı", "beklediğimden iyi",
    
    "süper", "efsane", "çok iyi", "tam istediğim", "bomba gibi",
    "canavar gibi", "üstüne yok", "on numara", "10 numara",
    "5 yıldız", "beş yıldız", "helal olsun", "bravo",
    "oha", "vay be", "eline sağlık",
    
    "beklediğim gibi", "pişman değilim", "değdi",
    "parasının karşılığı", "hak ediyor", "tam olması gerektiği gibi",
    "her kuruşuna değer", "tekrar alırım",
    
    "hızlı", "akıcı", "pürüzsüz", "stabil", "sorunsuz",
    "hızlıydı", "zamanında",
]

# ============================================================================
# NEGATİF KELİMELER 
# ============================================================================

NEGATIF_KELIMELER = [
    
    "berbat", "rezalet", "korkunç", "iğrenç", "felaket", "facia",
    "rezil", "skandal", "vahim", "işkence",
    
    "kötü", "bozuk", "yetersiz", "hayal kırıklığı", "vasat",
    "zayıf", "düşük", "başarısız", "sorunlu", "problemli",
    "eksik", "hatalı", "sıkıntılı",
    
    "pek iyi değil", "biraz sorunlu", "biraz kötü",
    "çok da iyi değil", "beklentimin altında",
    
    "beğenmedim", "pişman oldum", "iade ettim", "iade edeceğim",
    "şikayet ettim", "geri gönderdim", "razı değilim",
    "memnun değilim", "memnun kalmadım", "hoşlanmadım",
    
    "çalışmıyor", "bozuldu", "kırıldı", "donuyor", "kasıyor",
    "takılıyor", "kapanıyor", "açılmıyor", "yanıt vermiyor",
    "hata veriyor", "çöküyor", "yavaşlıyor", "ısınıyor",
    "arızalı", "defolu", "patladı", "söndü",
    
    "çöp", "bok gibi", "atmak lazım", "leş", "dandik",
    "yok artık", "saçmalık", "zırva", "boş",
    
    "dolandırıcılık", "sahte", "yanıltıcı", "fotoğraftaki gibi değil",
    "dolandırıldım", "kandırıldım", "kopya", "taklit",
    "reklam gibi değil", "açıklamayla uyuşmuyor",
    
    "pahalı", "geç", "yavaş", "ağır", "kırılgan",
    "pişmanım", "üzgünüm",
]
