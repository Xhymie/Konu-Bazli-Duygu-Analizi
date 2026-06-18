import os
import csv
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report
import joblib

from absa_pipeline import cumlelere_bol, cumledeki_aspectler, on_isleme

# ============================================================================
# AYARLAR
# ============================================================================
ETIKETLI_VERI_YOLU = r"../data/laptop_yorumlar_ai_labeled.csv"
MODEL_KAYIT_YOLU = r"../models/sentiment_model.pkl"
VECTORIZER_KAYIT_YOLU = r"../models/tfidf_vectorizer.pkl"

def veri_hazirla(csv_yolu):
    """
    CSV'den veriyi okur ve ML modelinin eğitilebileceği '[aspect] cümle' formatına dönüştürür.
    """
    X = []
    y = []
    
    with open(csv_yolu, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 3:
                sentiment = row[-1]
                aspect = row[-2]
                yorum = ",".join(row[:-2])
                
                
                if sentiment not in ["pozitif", "negatif", "notr"]:
                    continue
                    
                temiz_yorum = on_isleme(yorum)
                cumleler = cumlelere_bol(temiz_yorum)
                
                hedef_cumle = None
                
                
                for cumle in cumleler:
                    bulunanlar = cumledeki_aspectler(cumle)
                    
                    if aspect in bulunanlar or (aspect == "genel" and not bulunanlar):
                        hedef_cumle = cumle
                        break
                        
                
                if not hedef_cumle:
                    hedef_cumle = temiz_yorum
                    
                
                girdi_metni = f"[{aspect}] {hedef_cumle}"
                
                X.append(girdi_metni)
                y.append(sentiment)
                
    return X, y

def modelleri_egit_ve_kiyasla():
    """
    TF-IDF vektörleri üzerinden Logistic Regression ve Linear SVM modellerini eğitir ve karşılaştırır.
    En iyi modeli kaydeder.
    """
    print("Veri hazırlanıyor...")
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, ETIKETLI_VERI_YOLU)
    
    X, y = veri_hazirla(csv_path)
    print(f"Eğitim için kullanılacak toplam örnek sayısı: {len(X)}")
    
    print("\nTF-IDF vektörizasyonu yapılıyor...")
    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_tfidf = vectorizer.fit_transform(X)
    
    print("\nModel 1: Logistic Regression (class_weight='balanced')")
    lr_model = LogisticRegression(class_weight='balanced', max_iter=1000, random_state=42)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    lr_scores = cross_val_score(lr_model, X_tfidf, y, cv=cv, scoring='f1_macro')
    print(f"LR Macro F1 (CV): {lr_scores.mean():.4f} (+/- {lr_scores.std() * 2:.4f})")
    
    print("\nModel 2: Linear SVM (class_weight='balanced')")
    svm_model = LinearSVC(class_weight='balanced', random_state=42, dual=False)
    svm_scores = cross_val_score(svm_model, X_tfidf, y, cv=cv, scoring='f1_macro')
    print(f"SVM Macro F1 (CV): {svm_scores.mean():.4f} (+/- {svm_scores.std() * 2:.4f})")
    
    
    best_model_name = "Linear SVM" if svm_scores.mean() > lr_scores.mean() else "Logistic Regression"
    best_model = svm_model if svm_scores.mean() > lr_scores.mean() else lr_model
    
    print(f"\nSeçilen Model: {best_model_name}")
    print("Model tüm veri ile eğitiliyor ve kaydediliyor...")
    
    best_model.fit(X_tfidf, y)
    
    
    y_pred = best_model.predict(X_tfidf)
    print("\nEğitim Seti (Tüm Veri) Performansı:")
    print(classification_report(y, y_pred))
    
    
    models_dir = os.path.join(base_dir, "..", "models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        
    model_path = os.path.join(base_dir, MODEL_KAYIT_YOLU)
    vec_path = os.path.join(base_dir, VECTORIZER_KAYIT_YOLU)
    
    joblib.dump(best_model, model_path)
    joblib.dump(vectorizer, vec_path)
    
    print(f"-> Model başarıyla kaydedildi: {os.path.abspath(model_path)}")
    print(f"-> Vectorizer başarıyla kaydedildi: {os.path.abspath(vec_path)}")

if __name__ == "__main__":
    modelleri_egit_ve_kiyasla()
