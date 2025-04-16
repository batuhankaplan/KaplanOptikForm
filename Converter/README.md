# Belge Metin Dönüştürücü

Bu program, taranmış belgeleri (PDF, JPG, PNG, TIFF gibi) okuyup içindeki metinleri tanıyarak Word dosyasına dönüştürür.

## Özellikler

- PDF, JPG, PNG, TIFF ve BMP formatlarını destekler
- Türkçe ve İngilizce metin desteği
- Kolay kullanımlı grafiksel arayüz
- Dönüştürülen metinleri DOCX formatında kaydeder

## Gereksinimler

Bu programı çalıştırmak için aşağıdaki yazılımlara ihtiyacınız vardır:

1. **Python 3.7+** ([indirme linki](https://www.python.org/downloads/))
2. **Tesseract OCR** ([indirme linki](https://github.com/UB-Mannheim/tesseract/wiki))
3. **Poppler** ([indirme linki](https://github.com/oschwartz10612/poppler-windows/releases/))

## Kurulum

1. Bu depoyu bilgisayarınıza indirin veya klonlayın
2. Gerekli Python paketlerini kurun:
   ```
   pip install pytesseract pdf2image python-docx Pillow
   ```
3. Tesseract OCR'ı yükleyin ve yolunu ayarlayın:
   - Windows için Tesseract OCR indirip yükleyin
   - `converter.py` dosyasında `pytesseract.pytesseract.tesseract_cmd` değişkenini Tesseract kurulum yolunuza göre düzenleyin
4. Poppler'ı yükleyin:
   - İndirdiğiniz zip dosyasını çıkarın (örneğin: `C:\Program Files\poppler`)
   - Bin klasörünü PATH değişkeninize ekleyin veya
   - `converter.py` dosyasında `POPPLER_PATH` değişkenini güncelleyin

## Kullanım

Programı çalıştırmak için:

```
python converter.py
```

1. "Dosya Seç" butonuna tıklayarak dönüştürmek istediğiniz belgeyi seçin
2. Gerekirse çıktı dosyasının adını ve konumunu değiştirin
3. "Dönüştür" butonuna tıklayın
4. İşlem tamamlandığında, dönüştürülen metin belirtilen Word dosyasına kaydedilecektir

## Sorun Giderme

1. **"Tesseract is not installed or it's not in your PATH"**: Tesseract OCR'ın yolunu doğru ayarladığınızdan emin olun
2. **PDF dosyaları dönüştürülemiyorsa**: Poppler'ın yolunu doğru ayarladığınızdan emin olun
3. **Türkçe karakterler sorunluysa**: Tesseract'a Türkçe dil paketi yüklediğinizden emin olun

## Lisans

Bu proje açık kaynaklıdır. 