
"""
Olumsuzlama ve Bağlaç Sözlükleri
=================================
Olumsuzlama kelimeleri, kalıpları ve cümle bölme bağlaçları.
"""

# ============================================================================
# OLUMSUZLAMA KELİMELERİ 
# ============================================================================

OLUMSUZLAMA_KELIMELERI = [
    # --- Klasik olumsuzlama ---
    "değil", "değildi", "değilim", "değildir",
    "yok", "yoktu", "olmadı", "olmaz",
    # --- Fiil olumsuzlaması ---
    "etmez", "etmiyor", "yapmaz", "yapmıyor",
    "çalışmıyor", "gelmiyor", "olmuyor", "vermiyor",
    "tutmuyor", "yetmiyor", "demiyor",
    # --- Bağlamsal ---
    "hiç", "asla", "kesinlikle değil", "hiçbir şekilde",
    "hiçbir zaman", "katiyen", "sakın",
    "ne ... ne", "ne de",
    # --- mE- eki kontrol (olumsuz fiil takısı) ---
    "medi", "madı", "memiş", "mamış", "mez", "maz",
    "miyor", "muyor", "müyor", "mayor",
]

# ============================================================================
# OLUMSUZLAMA KALIPLARI
# Cümle bazında olumsuzlama tespiti için kullanılan ana kalıplar
# ============================================================================

OLUMSUZLAMA_KALIPLARI = [
    "değil", "değildi", "değilim", "değildir",
    "yok", "yoktu", "olmadı", "olmaz", "olmuyor",
    "hiç", "asla", "kesinlikle değil", "hiçbir şekilde",
]

# ============================================================================
# CÜMLE BÖLME BAĞLAÇLARI
# Karşıtlık/zıtlık bağlaçları — cümleyi sentiment açısından ikiye böler
# ============================================================================

BAGLACLAR = [
    "ama", "fakat", "ancak", "lakin",
    "bununla birlikte", "ne var ki", "yalnız",
]
