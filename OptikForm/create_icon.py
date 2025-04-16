import os
from PIL import Image

def create_ico_file():
    """PNG dosyasını ICO formatına dönüştürür"""
    try:
        # Icon logo dosyasının varlığını kontrol et
        if not os.path.exists('kaplan_optik_logo_icon.png'):
            print("Hata: kaplan_optik_logo_icon.png dosyası bulunamadı!")
            return False
        
        # PNG'yi ICO'ya dönüştür
        img = Image.open('kaplan_optik_logo_icon.png')
        # Icon boyutları
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save('kaplanlogo.ico', sizes=icon_sizes)
        
        print("kaplanlogo.ico başarıyla oluşturuldu!")
        return True
    except Exception as e:
        print(f"Hata: ICO dosyası oluşturulurken bir sorun oluştu: {e}")
        return False

if __name__ == "__main__":
    create_ico_file() 