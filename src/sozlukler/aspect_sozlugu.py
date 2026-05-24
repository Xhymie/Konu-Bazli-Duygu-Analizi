# -*- coding: utf-8 -*-
"""
Aspect Sözlüğü
==============
Her aspect için anahtar kelimeler.
Kategoriler: doğrudan isimler, fiil formları, argo/yazım hataları,
             bileşik ifadeler, dolaylı ifadeler.
"""

ASPECT_SOZLUGU = {
    "kargo": [
        # Doğrudan isimler
        "kargo", "teslimat", "kurye", "gönderim", "gönderi", "taşıma",
        "paket teslim", "teslim", "kargoci", "kargom",
        # Fiil formları
        "teslim edildi", "teslim aldım", "geldi", "ulaştı", "gönderildi",
        "teslim aldık", "elime ulaştı", "kapıma geldi",
        # Argo ve yazım hataları
        "kargoo", "kargp", "teslimt", "kargo firma",
        # Bileşik ifadeler
        "kargo süresi", "kargo hızı", "kargo firması", "teslimat süresi",
        "teslim süresi", "gönderim süresi", "kargo takip",
        # Dolaylı ifadeler (zaman + geldi/ulaştı kalıpları)
        "günde geldi", "günde ulaştı", "günde teslim", "günde elime",
        "saatte geldi", "haftada geldi", "geç geldi", "erken geldi",
        "hızlı geldi", "yavaş geldi", "zamanında geldi", "geç kaldı",
    ],

    "kalite": [
        # Doğrudan isimler
        "kalite", "kalitesi", "malzeme", "işçilik", "yapı", "build",
        "dayanıklılık", "sağlamlık", "plastik", "metal",
        # Fiil formları
        "bozuldu", "kırıldı", "çatladı", "dayandı", "dayanmadı",
        "beklediğim gibi", "beklediğimden",
        # Argo ve yazım hataları
        "kalitesiz", "kalitsiz", "kaliteli", "kalte",
        # Bileşik ifadeler
        "yapı kalitesi", "malzeme kalitesi", "ürün kalitesi", "build quality",
        "işçilik kalitesi", "kasa kalitesi",
        # Dolaylı ifadeler
        "ucuz plastik", "çıtçıt gibi", "sağlam duruyor", "sağlam değil",
        "dayanıklı", "çürük", "ince yapılmış", "kalın yapılmış",
        "premium hissiyat", "oyuncak gibi",
    ],

    "fiyat": [
        # Doğrudan isimler
        "fiyat", "fiyatı", "ücret", "para", "maliyet", "tutar",
        "bütçe", "taksit", "ödeme",
        # Fiil formları
        "ödedim", "harcadım", "aldım", "satın aldım",
        # Argo ve yazım hataları
        "fiat", "fyat", "fiyaat", "pahali", "ucz",
        # Bileşik ifadeler
        "fiyat performans", "para etmez", "parasının karşılığı",
        "fiyatına göre", "bu fiyata", "bu paraya", "eder mi",
        "fiyat dengesi", "değer fiyat", "para değer",
        # Dolaylı ifadeler
        "pahalı", "ucuz", "uygun", "ekonomik", "hesaplı", "makul fiyat",
        "kampanya", "indirim", "kupon", "indirimli", "kampanyalı",
        "fahiş", "kazık", "kelepir",
    ],

    "batarya": [
        # Doğrudan isimler
        "batarya", "pil", "şarj", "mah", "miliamper", "adaptör",
        "şarj aleti", "powerbank",
        # Fiil formları
        "şarj oluyor", "şarj olmuyor", "şarj tutuyor", "şarj tutmuyor",
        "bitiyor", "dayanıyor", "dayanmıyor", "tükeniyor",
        "dolması", "doluyor", "boşalıyor",
        # Argo ve yazım hataları
        "bater", "batary", "sarj", "şarjı", "pili", "bataryası",
        "şarjı", "pilleri",
        # Bileşik ifadeler
        "batarya ömrü", "pil ömrü", "şarj süresi", "batarya süresi",
        "şarj hızı", "hızlı şarj", "kablosuz şarj", "pil kapasitesi",
        # Dolaylı ifadeler
        "günde bitiyor", "saatte bitiyor", "gün dayanıyor", "saat gidiyor",
        "gün çıkarıyor", "gün götürüyor", "akşama kadar",
        "yarım günde", "tam gün", "iki gün",
    ],

    "ses_goruntu": [
        # Doğrudan isimler
        "ekran", "ses", "hoparlör", "mikrofon", "kamera", "lcd", "oled",
        "amoled", "ips", "çözünürlük", "piksel", "fps",
        # Fiil formları
        "duyuluyor", "duyulmuyor", "görünüyor", "görüntülüyor",
        "çekiyor", "fotoğraf çekiyor",
        # Argo ve yazım hataları
        "hopalör", "hoperlör", "mikrafon", "kamerasI", "ekranı",
        # Bileşik ifadeler
        "ses kalitesi", "görüntü kalitesi", "ekran kalitesi",
        "kamera kalitesi", "video kalitesi", "fotoğraf kalitesi",
        "ekran parlaklığı", "ekran rengi", "renk doğruluğu",
        # Dolaylı ifadeler
        "parlak ekran", "canlı renkler", "soluk ekran", "donuk ekran",
        "net görüntü", "bulanık", "titreşim", "speaker",
        "fotoğraf", "video", "selfie", "ön kamera", "arka kamera",
        "megapiksel", "parlaklık", "renk",
    ],

    "ambalaj": [
        # Doğrudan isimler
        "ambalaj", "paket", "kutu", "paketleme", "ambalajlama",
        "poşet", "karton", "streç", "balonlu",
        # Fiil formları
        "paketlenmiş", "sarılmış", "korunmuş", "ezilmiş", "açıldı",
        "kutudan çıktı", "kutudan çıkan",
        # Argo ve yazım hataları
        "amblaj", "ambalj", "paketi", "kutusu",
        # Bileşik ifadeler
        "kutu içeriği", "kutu tasarımı", "paket içeriği",
        "ambalaj kalitesi", "orijinal kutu",
        # Dolaylı ifadeler
        "şık kutu", "sağlam kutu", "aksesuar", "kulak içi", "kılıf",
        "adaptör kutu", "koruyucu", "bubble wrap", "içinden çıkanlar",
        "hediye gibi", "güzel paketlenmiş", "özensiz paketlenmiş",
    ],

    "genel": [
        # Doğrudan isimler
        "genel", "genelde", "genelinde", "ürün", "cihaz", "telefon",
        "tablet", "laptop", "ürünü",
        # Fiil formları
        "memnunum", "memnun kaldım", "tavsiye ederim", "öneririm",
        "pişmanım", "pişman oldum", "aldığıma sevindim",
        "tekrar alırım", "almam", "almazdım",
        # Bileşik ifadeler
        "genel olarak", "sonuç olarak", "toparlarsak", "özetle",
        "genel değerlendirme", "genel izlenim",
        # Dolaylı ifadeler
        "yıldız", "puan", "not veriyorum", "puanlıyorum",
        "her şey", "her şeyi", "bütünüyle", "toplamda",
        "değer", "tam puan",
    ],
}
