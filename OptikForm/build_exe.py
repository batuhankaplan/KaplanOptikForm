import os
import subprocess
import shutil
from create_icon import create_ico_file
from create_logo import create_logo

def build_exe():
    """
    PyInstaller kullanarak uygulamanın exe dosyasını oluşturur.
    Öncelikle kaplanlogo.ico'yu oluşturur ve daha sonra onu kullanarak exe oluşturur.
    """
    print("Kaplan Optik Form Uygulaması exe oluşturma işlemi başlıyor...")
    
    # Önce logo dosyalarını kopyala/hazırla
    print("Kaplan logoları hazırlanıyor...")
    create_logo()
    
    # Ico dosyasını oluştur
    icon_created = create_ico_file()
    if not icon_created:
        print("Uyarı: İkon dosyası oluşturulamadı. Varsayılan ikon kullanılacak.")
        icon_path = ""
    else:
        icon_path = os.path.abspath("kaplanlogo.ico")
        print(f"İkon dosyası: {icon_path}")
    
    # PyInstaller komutunu hazırla
    pyinstaller_cmd = [
        "pyinstaller",
        "--name=KaplanOptikForm",
        "--onefile",
        "--noconsole",
        f"--icon={icon_path}" if icon_path else "",
        "--add-data=kaplanlogo.png;.",
        "--add-data=kaplanlogo_icon.png;.",
        "main.py"
    ]
    
    # Boş parametreleri temizle
    pyinstaller_cmd = [cmd for cmd in pyinstaller_cmd if cmd]
    
    try:
        # PyInstaller komutunu çalıştır
        subprocess.run(pyinstaller_cmd, check=True)
        
        print("\nExe dosyası başarıyla oluşturuldu!")
        print("Exe dosyası: dist/KaplanOptikForm.exe")
        
        # Klasör oluşturma
        os.makedirs("KaplanOptikForm", exist_ok=True)
        
        # Dosyaları kopyala
        shutil.copy("dist/KaplanOptikForm.exe", "KaplanOptikForm/")
        shutil.copy("kaplanlogo.png", "KaplanOptikForm/")
        shutil.copy("kaplanlogo_icon.png", "KaplanOptikForm/")
        
        # test_results klasörünü oluştur
        os.makedirs("KaplanOptikForm/test_results", exist_ok=True)
        
        print("\nKaplanOptikForm klasörü hazırlandı.")
        print("Program bu klasörden çalıştırılabilir.")
        
    except Exception as e:
        print(f"Hata: Exe oluşturma işlemi başarısız: {e}")

def create_test_ico():
    """PNG dosyasını ICO formatına dönüştürür"""
    try:
        # Png dosyasının varlığını kontrol et
        if not os.path.exists('test_logo.png'):
            print("Hata: test_logo.png dosyası bulunamadı!")
            return False
        
        # PNG'yi ICO'ya dönüştür
        from PIL import Image
        img = Image.open('test_logo.png')
        # Icon boyutları
        icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        img.save('test_logo.ico', sizes=icon_sizes)
        
        print("test_logo.ico başarıyla oluşturuldu!")
        return True
    except Exception as e:
        print(f"Hata: ICO dosyası oluşturulurken bir sorun oluştu: {e}")
        return False

if __name__ == "__main__":
    build_exe() 