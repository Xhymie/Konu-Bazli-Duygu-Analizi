# -*- coding: utf-8 -*-
"""
Yöntem 1.5 Değerlendirme Sistemi:
Hibrit sistemin (Kural tabanlı aspect + ML sentiment) test edilmesini sağlar.
"""

import os
import csv
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix

from hybrid_pipeline import hybrid_absa_pipeline

# ============================================================================
# AYARLAR (PATH TANIMLAMALARI)
# ============================================================================
ETIKETLI_VERI_YOLU = r"../data/laptop_yorumlar_ai_labeled.csv"
CIKIS_KLASORU = "../visuals/yontem1_5"
TAHMIN_CSV_YOLU = r"../data/laptop_yorumlar_yontem1_5_tahminler.csv"

def degerlendir_ve_raporla(etiketli_yolu, cikis_klasoru, tahmin_kayit_yolu):
    """Sistemi değerlendirir, metrikleri basar ve sonuç grafiklerini üretir."""
    print("\n--- Yöntem 1.5 Değerlendirme ve Görselleştirme İşlemleri ---")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    etiketli_yolu = os.path.join(base_dir, etiketli_yolu)
    cikis_klasoru = os.path.join(base_dir, cikis_klasoru)
    tahmin_kayit_yolu = os.path.join(base_dir, tahmin_kayit_yolu)
    
    if not os.path.exists(etiketli_yolu):
        print(f"Hata: {etiketli_yolu} bulunamadı!")
        return
        
    if not os.path.exists(cikis_klasoru):
        os.makedirs(cikis_klasoru)
        
    # 2.1 Gerçek verileri yükle ve hatalı virgülden bölünen yorumları birleştir
    ground_truth = defaultdict(dict)  # {yorum: {aspect: sentiment}}
    all_data = []
    
    with open(etiketli_yolu, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # Header'ı geç
        for row in reader:
            if len(row) >= 3:
                sentiment = row[-1]
                aspect = row[-2]
                yorum = ",".join(row[:-2])
                
                ground_truth[yorum][aspect] = sentiment
                all_data.append([yorum, aspect, sentiment])
                
    print(f"Toplam benzersiz etiketli yorum sayısı: {len(ground_truth)}")
    
    # 2.2 Pipeline'ı Çalıştır ve Tahminleri Topla
    aspects = ["kargo", "kalite", "fiyat", "batarya", "ses_goruntu", "ambalaj", "genel"]
    
    y_true = []
    y_pred = []
    
    # Tahminleri CSV'ye kaydetmek için liste
    tahmin_satirlari = []
    
    print("Sistem çalıştırılıyor (Yöntem 1.5 - Hibrit)...")
    for yorum, gt_labels in ground_truth.items():
        # Pipeline'dan tahminleri al
        predictions = hybrid_absa_pipeline(yorum)
        pred_labels = {}
        for asp, sent, _, _ in predictions:
            pred_labels[asp] = sent
            
        # Her aspect için karşılaştırma yap
        for asp in aspects:
            true_sent = gt_labels.get(asp, "yok")
            pred_sent = pred_labels.get(asp, "yok")
            
            y_true.append(true_sent)
            y_pred.append(pred_sent)
            
            # CSV için satır ekle
            if true_sent != "yok" or pred_sent != "yok":
                tahmin_satirlari.append([yorum, asp, true_sent, pred_sent])

    # 2.3 Tahminleri CSV Olarak Kaydet (Kullanıcının İsteği)
    with open(tahmin_kayit_yolu, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["yorum", "aspect", "gercek_sentiment", "tahmin_sentiment"])
        writer.writerows(tahmin_satirlari)
    print(f"-> Yöntem 1.5 tahminleri kaydedildi: {tahmin_kayit_yolu}")

    # 2.4 Metrikleri Hesapla (Hocanın İstediği Madde 3.6)
    print("\n" + "="*40)
    print("YÖNTEM 1.5 DEĞERLENDİRME SONUÇLARI (METRİKLER)")
    print("="*40)
    
    accuracy = accuracy_score(y_true, y_pred)
    print(f"Genel Doğruluk (Accuracy): %{accuracy*100:.2f}\n")
    
    labels = ["yok", "pozitif", "negatif", "notr"]
    report = classification_report(y_true, y_pred, labels=labels, target_names=labels, zero_division=0)
    print(report)

    # 2.5 Grafikleri Üret (Ekran Görüntüsündeki İsimlerle)
    
    # Grafik 3: Karmaşıklık Matrisi (sonuc_karmasiklik_matrisi.png)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title('Yöntem 1.5 Karmaşıklık Matrisi (Confusion Matrix)', fontsize=14)
    plt.xlabel('Tahmin Edilen', fontsize=12)
    plt.ylabel('Gerçek', fontsize=12)
    plt.tight_layout()
    path = os.path.join(cikis_klasoru, 'sonuc_karmasiklik_matrisi_1_5.png')
    plt.savefig(path)
    plt.close()
    print(f"-> Grafik kaydedildi: {path}")

if __name__ == "__main__":
    degerlendir_ve_raporla(ETIKETLI_VERI_YOLU, CIKIS_KLASORU, TAHMIN_CSV_YOLU)
    print("\nTüm işlemler tamamlandı. Yöntem 1.5 grafikleri 'visuals/yontem1_5' klasöründe.")
