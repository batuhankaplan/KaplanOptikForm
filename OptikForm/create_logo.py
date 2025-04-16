import shutil
import os

def create_logo():
    """
    Kaplan Optik logolarını kopyalar ve kullanım için hazırlar
    """
    # Normal logo için
    shutil.copy("kaplan_optik_logo_normal.png", "kaplanlogo.png")
    
    # Icon için
    shutil.copy("kaplan_optik_logo_icon.png", "kaplanlogo_icon.png")
    
    print("Kaplan logo başarıyla oluşturuldu: kaplanlogo.png")
    print("Kaplan icon başarıyla oluşturuldu: kaplanlogo_icon.png")
    
    return True

if __name__ == "__main__":
    create_logo() 