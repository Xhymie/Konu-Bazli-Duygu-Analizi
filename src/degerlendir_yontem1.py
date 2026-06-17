# -*- coding: utf-8 -*-
"""
Yöntem 1 (Kural Tabanlı) Değerlendirme ve Görselleştirme Sistemi
===============================================================
Bu script; EDA analizi yapar, WordCloud üretir, sistemi değerlendirir,
metrikleri hesaplar ve sonuçları görselleştirir.

Hocanın istediği tüm maddeleri (3.3, 3.4, 3.6, 3.7) karşılar.
"""

import os
import csv
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from wordcloud import WordCloud
from absa_pipeline import absa_pipeline

# ============================================================================
# AYARLAR (PATH TANIMLAMALARI)
# CSV dosyaları değiştikçe sadece burayı güncellemeniz yeterlidir.
# ============================================================================
HAM_VERI_YOLU = r"data/test.csv"
ETIKETLI_VERI_YOLU = r"data/test.csv"
CIKIS_KLASORU = "visuals"
TAHMIN_CSV_YOLU = r"data/test_yontem1.csv"

# Laptop yorumlarının bulunduğu satır aralığı (Pandas indexi olarak)
# Satır 1002-1751 arası -> Index 1000-1750 arası
START_INDEX = 0
END_INDEX = 512


def eda_ve_wordcloud(ham_yolu, cikis_klasoru):
    """Ham veriden yorum uzunluğu dağılımı ve WordCloud üretir."""
    print("\n--- 1. EDA ve WordCloud İşlemleri ---")
    
    if not os.path.exists(ham_yolu):
        print(f"Uyarı: {ham_yolu} bulunamadı. EDA adımı atlanıyor.")
        return
        
    # Ham veriyi oku
    df_all = pd.read_csv(ham_yolu)
    
    # Sadece laptop yorumlarını al (Kullanıcının isteği üzerine)
    df_ham = df_all.iloc[START_INDEX:END_INDEX]
    print(f"Ham veriden {len(df_ham)} satır (laptop yorumları) alındı.")
    
    # 1.1 Yorum Uzunluğu Dağılımı (Hocanın İstediği Madde 3.3 & 3.7)
    if 'text' in df_ham.columns:
        df_ham['yorum_uzunlugu'] = df_ham['text'].apply(lambda x: len(str(x).split()))
        
        plt.figure(figsize=(10, 6))
        sns.histplot(df_ham['yorum_uzunlugu'], bins=20, kde=True, color='skyblue')
        plt.title('Yorum Uzunlukları Dağılımı (Kelime Sayısı) - Ham Veri', fontsize=14)
        plt.xlabel('Kelime Sayısı', fontsize=12)
        plt.ylabel('Frekans', fontsize=12)
        plt.tight_layout()
        
        path = os.path.join(cikis_klasoru, 'eda_yorum_uzunlugu_dagilimi.png')
        plt.savefig(path)
        plt.close()
        print(f"-> Grafik kaydedildi: {path}")
        
        # 1.2 WordCloud (Genel Kelime Bulutu)
        all_text = " ".join(df_ham['text'].dropna().astype(str))
        
        # Türkçe stop words (basit liste)
        stop_words = ["ve", "veya", "ama", "fakat", "lakin", "ile", "bir", "bu", "da", "de", "için", "çok", "en", "ki"]
        
        wordcloud = WordCloud(
            width=800, height=400,
            background_color='white',
            stopwords=set(stop_words),
            min_font_size=10
        ).generate(all_text)
        
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.title("En Çok Geçen Kelimeler (WordCloud)", fontsize=14)
        plt.tight_layout(pad=0)
        
        wc_path = os.path.join(cikis_klasoru, 'wordcloud_general.png')
        plt.savefig(wc_path)
        plt.close()
        print(f"-> WordCloud kaydedildi: {wc_path}")
    else:
        print("Uyarı: Ham veride 'text' sütunu bulunamadı.")


def degerlendir_ve_raporla(etiketli_yolu, cikis_klasoru, tahmin_kayit_yolu):
    """Sistemi değerlendirir, metrikleri basar ve sonuç grafiklerini üretir."""
    print("\n--- 2. Değerlendirme ve Görselleştirme İşlemleri ---")
    
    if not os.path.exists(etiketli_yolu):
        print(f"Hata: {etiketli_yolu} bulunamadı!")
        return
        
    # 2.1 Gerçek Verileri Yükle (Ground Truth)
    # CSV'de yorumlar tırnak içine alınmadığı için virgül içeren yorumlar bölünmüş olabilir.
    # Bu yüzden son iki sütunu (aspect, sentiment) alıp kalanları yorum olarak birleştiriyoruz.
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
    
    # Pandas DataFrame'ini manuel oluşturuyoruz (ParserError'ı engellemek için)
    df_labeled = pd.DataFrame(all_data, columns=["yorum", "aspect", "sentiment"])
    
    # Grafik 1: Gerçek Verilerdeki Aspect Dağılımı (Hocanın İstediği)
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df_labeled, x='aspect', order=df_labeled['aspect'].value_counts().index, palette='viridis')
    plt.title('Veri Setindeki Gerçek Aspect Dağılımı (Ground Truth)', fontsize=14)
    plt.xlabel('Aspect', fontsize=12)
    plt.ylabel('Frekans', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    path = os.path.join(cikis_klasoru, 'eda_aspect_dagilimi.png')
    plt.savefig(path)
    plt.close()
    print(f"-> Grafik kaydedildi: {path}")

    # 2.2 Pipeline'ı Çalıştır ve Tahminleri Topla
    aspects = ["kargo", "kalite", "fiyat", "batarya", "ses_goruntu", "ambalaj", "genel"]
    
    y_true = []
    y_pred = []
    
    # Tahminleri CSV'ye kaydetmek için liste
    tahmin_satirlari = []
    
    print("Sistem çalıştırılıyor (Yöntem 1)...")
    for yorum, gt_labels in ground_truth.items():
        # Pipeline'dan tahminleri al
        predictions = absa_pipeline(yorum)
        pred_labels = {}
        for asp, sent, _, _ in predictions:
            pred_labels[asp] = sent
            
        # Her aspect için karşılaştırma yap
        for asp in aspects:
            true_sent = gt_labels.get(asp, "yok")
            pred_sent = pred_labels.get(asp, "yok")
            
            # GERÇEKTE "yok" olanları değerlendirme testinden çıkar
            # Böylece sadece saf duygu analizi başarısını ölçeriz
            if true_sent == "yok":
                continue
            
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
    print(f"-> Yöntem 1 tahminleri kaydedildi: {tahmin_kayit_yolu}")

    # 2.4 Metrikleri Hesapla (Hocanın İstediği Madde 3.6)
    print("\n" + "="*40)
    print("DEĞERLENDİRME SONUÇLARI (METRİKLER)")
    print("="*40)
    
    accuracy = accuracy_score(y_true, y_pred)
    print(f"Duygu Analizi Doğruluğu (Accuracy - 'Yok' Sınıfı Hariç): %{accuracy*100:.2f}\n")
    
    labels = ["pozitif", "negatif", "notr"]
    report = classification_report(y_true, y_pred, labels=labels, target_names=labels, zero_division=0)
    print(report)

    # 2.5 Grafikleri Üret (Ekran Görüntüsündeki İsimlerle)
    
    # Grafik 3: Karmaşıklık Matrisi (sonuc_karmasiklik_matrisi.png)
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title('Karmaşıklık Matrisi (Confusion Matrix)', fontsize=14)
    plt.xlabel('Tahmin Edilen', fontsize=12)
    plt.ylabel('Gerçek', fontsize=12)
    plt.tight_layout()
    path = os.path.join(cikis_klasoru, 'sonuc_karmasiklik_matrisi.png')
    plt.savefig(path)
    plt.close()
    print(f"-> Grafik kaydedildi: {path}")

    # Grafik 4: Tahmin Edilen Aspect Frekansları (sonuc_aspect_frekanslari.png)
    pred_df = pd.DataFrame(tahmin_satirlari, columns=["yorum", "aspect", "gercek", "tahmin"])
    valid_preds = pred_df[pred_df['tahmin'] != "yok"]
    
    plt.figure(figsize=(10, 6))
    sns.countplot(data=valid_preds, x='aspect', order=aspects, palette='Set2')
    plt.title('Tahmin Edilen Aspect Frekansları', fontsize=14)
    plt.xlabel('Aspect', fontsize=12)
    plt.ylabel('Frekans', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    path = os.path.join(cikis_klasoru, 'sonuc_aspect_frekanslari.png')
    plt.savefig(path)
    plt.close()
    print(f"-> Grafik kaydedildi: {path}")

    # Grafik 5: Aspect Duygu Dağılımı (sonuc_aspect_sentiment_dagilimi.png)
    plt.figure(figsize=(12, 6))
    duygu_renkleri = {'pozitif': '#2ecc71', 'negatif': '#e74c3c', 'notr': '#95a5a6'}
    sns.countplot(data=valid_preds, x='aspect', hue='tahmin', order=aspects, palette=duygu_renkleri)
    plt.title('Aspect Başına Tahmin Edilen Duygu Dağılımı', fontsize=14)
    plt.xlabel('Aspect', fontsize=12)
    plt.ylabel('Frekans', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(title='Duygu')
    plt.tight_layout()
    path = os.path.join(cikis_klasoru, 'sonuc_aspect_sentiment_dagilimi.png')
    plt.savefig(path)
    plt.close()
    print(f"-> Grafik kaydedildi: {path}")


if __name__ == "__main__":
    if not os.path.exists(CIKIS_KLASORU):
        os.makedirs(CIKIS_KLASORU)
        
    # 1. EDA ve WordCloud
    eda_ve_wordcloud(HAM_VERI_YOLU, CIKIS_KLASORU)
    
    # 2. Değerlendirme ve Grafikler
    degerlendir_ve_raporla(ETIKETLI_VERI_YOLU, CIKIS_KLASORU, TAHMIN_CSV_YOLU)
    
    print("\nTüm işlemler tamamlandı. Grafikler 'visuals/' klasöründe.")
