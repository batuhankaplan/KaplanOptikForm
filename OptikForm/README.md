# Optik Form Uygulaması

Bu uygulama, interaktif bir optik form sistemi sunar. Öğrenciler veya sınav yapan kişiler için tasarlanmış bu uygulama ile test oluşturabilir, yanıtları işaretleyebilir ve sonuçları görebilirsiniz.

## Özellikler

- Her test 20 sorudan oluşur, her soru 5 şıklıdır (A, B, C, D, E)
- Şık işaretleme ve renk düzeni:
  - İşaretlenen şıklar yeşil renkle vurgulanır
  - Sınav bittiğinde: 
    - Doğru cevaplar yeşil tik ile gösterilir
    - Yanlış cevaplar kırmızı tik ile gösterilir
    - Yanlış şıklar kırmızıya dönüşür
  - Boş bırakılan sorular daha sonra doldurulursa mavi renkte gösterilir
- Puanlama sistemi:
  - Her test için "Kaç yanlış bir doğruyu götürür?" ayarı belirlenebilir
  - Puanlama formülü: `[(Doğru Sayısı - (Yanlış Sayısı / Yanlış Götürme Oranı)) / Toplam Soru Sayısı] x 100`
- Birden fazla test sekmesi açabilme özelliği
- Test sonuçlarının kaydedilmesi

## Kurulum

1. Gerekli bağımlılıkları yükleyin:
```
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```
python main.py
```

## Kullanım

1. Test başlığını ve "Kaç yanlış bir doğruyu götürür?" değerini ayarlayın
2. Soruları yanıtlayın (A, B, C, D, E şıklarından birini seçin)
3. "Sınavı Bitir" butonuna tıklayın
4. Test sonuçlarınızı görüntüleyin
5. Yeni bir test için "Yeni Test" butonuna tıklayın veya "+" simgesine tıklayarak yeni bir test sekmesi açın

## Notlar

- Test sonuçları "test_results" klasöründe JSON formatında saklanır
- Her testin bilgileri: başlık, tarih, puan, doğru sayısı, yanlış sayısı, boş sayısı ve yanlış götürme oranı olarak kaydedilir

## Exe Dosyası Oluşturma

Uygulamanın exe dosyasını oluşturmak için aşağıdaki adımları izleyin:

1. Gerekli paketleri yükleyin:
```
pip install -r requirements.txt
```

2. Kaplan logo png dosyasını oluşturun:
```
python create_logo.py
```

3. Exe dosyasını oluşturun:
```
python build_exe.py
```

4. İşlem tamamlandığında, `KaplanOptikForm` klasöründe çalıştırılabilir exe dosyasını bulacaksınız.

## İkon Bilgileri

Uygulama ikonu (kaplanlogo.png) otomatik olarak:
- Uygulama pencere ikonu
- Exe dosyası ikonu
olarak kullanılacaktır. 