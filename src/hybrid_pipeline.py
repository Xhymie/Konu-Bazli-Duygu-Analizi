
"""
Yöntem 1.5: Hibrit ABSA Pipeline
=================================
Aspect tespiti kural tabanlı, sentiment tespiti ise eğitilmiş TF-IDF + LR/SVM
modeli kullanılarak gerçekleştirilir.
"""

import os
import joblib

from absa_pipeline import on_isleme, cumlelere_bol, cumledeki_aspectler
from sozlukler import ASPECT_SOZLUGU


_MODEL = None
_VECTORIZER = None

def _modeli_yukle():
    """Model ve vectorizer'ı belleğe yükler (Lazy load)."""
    global _MODEL, _VECTORIZER
    if _MODEL is None or _VECTORIZER is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        model_path = os.path.join(base_dir, "..", "models", "sentiment_model.pkl")
        vec_path = os.path.join(base_dir, "..", "models", "tfidf_vectorizer.pkl")
        
        if not os.path.exists(model_path) or not os.path.exists(vec_path):
            raise FileNotFoundError("Model dosyaları bulunamadı! Önce 'sentiment_tfidf.py' çalıştırılmalı.")
            
        _MODEL = joblib.load(model_path)
        _VECTORIZER = joblib.load(vec_path)

def ml_sentiment_hesapla(aspect, cumle):
    """
    Eğitilmiş makine öğrenmesi modelini kullanarak cümlenin duygu durumunu hesaplar.
    Girdi formatı eğitim setiyle aynı: "[aspect] cümle"
    """
    _modeli_yukle()
    
    girdi = f"[{aspect}] {cumle}"
    X_tfidf = _VECTORIZER.transform([girdi])
    
    sentiment = _MODEL.predict(X_tfidf)[0]
    
    skor = 0
    if hasattr(_MODEL, "predict_proba"):
        probs = _MODEL.predict_proba(X_tfidf)[0]
        skor = max(probs)
    elif hasattr(_MODEL, "decision_function"):
        skor = max(abs(_MODEL.decision_function(X_tfidf)[0]))
        
    return sentiment, skor

def hybrid_absa_pipeline(yorum_metni):
    """
    Hibrit ABSA pipeline fonksiyonu.
    Kural tabanlı aspect bulur, sentiment'i ML modeli ile tahmin eder.

    Args:
        yorum_metni (str): Ham yorum metni

    Returns:
        list of tuple: [(aspect, sentiment, cumle, skor), ...]
    """
    temiz_metin = on_isleme(yorum_metni)
    cumleler = cumlelere_bol(temiz_metin)
    
    sonuclar = []
    herhangi_aspect_bulundu = False

    for cumle in cumleler:
        aspectler = cumledeki_aspectler(cumle)

        if aspectler:
            herhangi_aspect_bulundu = True
            for asp in aspectler:
                sentiment, skor = ml_sentiment_hesapla(asp, cumle)
                sonuclar.append((asp, sentiment, cumle, skor))
        else:
            
            cumle_lower = cumle.lower()
            genel_bulundu = False
            for kelime in ASPECT_SOZLUGU["genel"]:
                if kelime.lower() in cumle_lower:
                    genel_bulundu = True
                    break
            
            if genel_bulundu:
                herhangi_aspect_bulundu = True
                sentiment, skor = ml_sentiment_hesapla("genel", cumle)
                sonuclar.append(("genel", sentiment, cumle, skor))

    
    if not herhangi_aspect_bulundu:
        sentiment, skor = ml_sentiment_hesapla("genel", temiz_metin)
        sonuclar.append(("genel", sentiment, temiz_metin, skor))

    return sonuclar
