# -*- coding: utf-8 -*-
"""
Sözlükler Paketi
================
Tüm ABSA sözlüklerini tek bir yerden dışa aktarır.

Kullanım:
    from sozlukler import ASPECT_SOZLUGU, POZITIF_KELIMELER, NEGATIF_KELIMELER
"""

from sozlukler.aspect_sozlugu import ASPECT_SOZLUGU
from sozlukler.sentiment_sozlugu import POZITIF_KELIMELER, NEGATIF_KELIMELER
from sozlukler.olumsuzlama import (
    OLUMSUZLAMA_KELIMELERI,
    OLUMSUZLAMA_KALIPLARI,
    BAGLACLAR,
)
