import os
import json
import pytesseract
from PIL import Image
from pdf2image import convert_from_path
import docx
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# Varsayılan yapılandırma
DEFAULT_CONFIG = {
    "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    "poppler_path": r"C:\Program Files\poppler\bin"
}

# Yapılandırma dosyası yolu
CONFIG_FILE = "converter_config.json"

def load_config():
    """Yapılandırma dosyasını yükler veya varsayılanı oluşturur"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Yapılandırma yüklenemedi: {str(e)}")
    
    # Varsayılan yapılandırmayı yaz ve döndür
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG

def save_config(config):
    """Yapılandırmayı dosyaya kaydeder"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"Yapılandırma kaydedilemedi: {str(e)}")

# Yapılandırmayı yükle
config = load_config()

# Tesseract yolunu ayarla
pytesseract.pytesseract.tesseract_cmd = config["tesseract_path"]

# Poppler yolu
POPPLER_PATH = config["poppler_path"]

class DocumentConverter:
    def __init__(self):
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp']
        # Kullanılabilir diller, Tesseract'a yüklenen dil paketlerine göre değişir
        self.languages = ['tur', 'eng']  # Varsayılan olarak Türkçe ve İngilizce
    
    def extract_text_from_image(self, image):
        """Görüntüden metin çıkarır"""
        try:
            # Önce tüm dilleri kullanarak dene
            text = pytesseract.image_to_string(image, lang='+'.join(self.languages))
            return text
        except Exception as e:
            # Hata durumunda sadece İngilizce ile dene
            try:
                text = pytesseract.image_to_string(image, lang='eng')
                return text
            except Exception as inner_e:
                # Son çare olarak dil belirtmeden dene
                return pytesseract.image_to_string(image)
    
    def process_pdf(self, pdf_path):
        """PDF'i işler ve metin çıkarır"""
        pages = convert_from_path(pdf_path, 300, poppler_path=POPPLER_PATH)
        text = ""
        
        for page in pages:
            text += self.extract_text_from_image(page) + "\n\n"
        
        return text
    
    def process_image(self, image_path):
        """Görüntü dosyasını işler ve metin çıkarır"""
        with Image.open(image_path) as img:
            text = self.extract_text_from_image(img)
        return text
    
    def save_to_word(self, text, output_path):
        """Metni Word dosyasına kaydeder"""
        doc = docx.Document()
        doc.add_paragraph(text)
        doc.save(output_path)
        
    def convert(self, input_path, output_path=None):
        """Dosyayı dönüştürür ve Word olarak kaydeder"""
        file_ext = os.path.splitext(input_path)[1].lower()
        
        if file_ext not in self.supported_formats:
            raise ValueError(f"Desteklenmeyen dosya formatı: {file_ext}")
        
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = f"{base_name}_converted.docx"
        
        try:
            if file_ext == '.pdf':
                text = self.process_pdf(input_path)
            else:
                text = self.process_image(input_path)
            
            self.save_to_word(text, output_path)
            return output_path
        except Exception as e:
            raise Exception(f"Dönüştürme sırasında hata: {str(e)}")

class SettingsDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Ayarlar")
        self.dialog.geometry("500x200")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Ayarları yükle
        self.config = load_config()
        
        # Tesseract yolu
        tesseract_frame = ttk.Frame(self.dialog, padding=10)
        tesseract_frame.pack(fill=tk.X)
        
        ttk.Label(tesseract_frame, text="Tesseract yolu:").pack(side=tk.LEFT, padx=5)
        self.tesseract_var = tk.StringVar(value=self.config["tesseract_path"])
        ttk.Entry(tesseract_frame, textvariable=self.tesseract_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(tesseract_frame, text="...", command=self.browse_tesseract).pack(side=tk.LEFT, padx=5)
        
        # Poppler yolu
        poppler_frame = ttk.Frame(self.dialog, padding=10)
        poppler_frame.pack(fill=tk.X)
        
        ttk.Label(poppler_frame, text="Poppler bin yolu:").pack(side=tk.LEFT, padx=5)
        self.poppler_var = tk.StringVar(value=self.config["poppler_path"])
        ttk.Entry(poppler_frame, textvariable=self.poppler_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(poppler_frame, text="...", command=self.browse_poppler).pack(side=tk.LEFT, padx=5)
        
        # Butonlar
        button_frame = ttk.Frame(self.dialog, padding=10)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Kaydet", command=self.save).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="İptal", command=self.cancel).pack(side=tk.RIGHT, padx=5)
    
    def browse_tesseract(self):
        path = filedialog.askopenfilename(
            title="Tesseract uygulamasını seçin",
            filetypes=[("Executable", "*.exe"), ("Tüm Dosyalar", "*.*")]
        )
        if path:
            self.tesseract_var.set(path)
    
    def browse_poppler(self):
        path = filedialog.askdirectory(
            title="Poppler bin klasörünü seçin"
        )
        if path:
            self.poppler_var.set(path)
    
    def save(self):
        new_config = {
            "tesseract_path": self.tesseract_var.get(),
            "poppler_path": self.poppler_var.get()
        }
        
        # Yapılandırmayı kaydet
        save_config(new_config)
        
        # Yapılandırmayı güncelle
        global config, POPPLER_PATH
        config = new_config
        pytesseract.pytesseract.tesseract_cmd = config["tesseract_path"]
        POPPLER_PATH = config["poppler_path"]
        
        messagebox.showinfo("Bilgi", "Ayarlar kaydedildi!\nYeni ayarları uygulamak için programı yeniden başlatmanız gerekebilir.")
        self.dialog.destroy()
    
    def cancel(self):
        self.dialog.destroy()

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Belge Metin Dönüştürücü")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        self.converter = DocumentConverter()
        self.setup_ui()
    
    def setup_ui(self):
        # Ana frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        ttk.Label(main_frame, text="Belge Metin Dönüştürücü", font=("Arial", 16)).pack(pady=10)
        ttk.Label(main_frame, text="PDF, JPG, PNG ve TIFF dosyalarından metin çıkarır").pack(pady=5)
        
        # Dosya seçim butonu
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=20)
        
        self.file_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.file_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="Dosya Seç", command=self.select_file).pack(side=tk.LEFT, padx=5)
        
        # Çıktı dosyası
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.X, pady=10)
        
        self.output_var = tk.StringVar()
        ttk.Label(output_frame, text="Çıktı dosyası:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(output_frame, textvariable=self.output_var, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="...", command=self.select_output).pack(side=tk.LEFT, padx=5)
        
        # Dönüştür ve ayarlar butonları
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Dönüştür", command=self.convert).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Ayarlar", command=self.open_settings).pack(side=tk.LEFT, padx=10)
        
        # İlerleme çubuğu
        self.progress = ttk.Progressbar(main_frame, mode="indeterminate")
        self.progress.pack(fill=tk.X, pady=10)
        
        # Durum mesajı
        self.status_var = tk.StringVar()
        self.status_var.set("Hazır")
        ttk.Label(main_frame, textvariable=self.status_var).pack(pady=5)
    
    def open_settings(self):
        SettingsDialog(self.root)
    
    def select_file(self):
        filetypes = [
            ("Desteklenen Dosyalar", "*.pdf;*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.bmp"),
            ("PDF Dosyaları", "*.pdf"),
            ("Resim Dosyaları", "*.jpg;*.jpeg;*.png;*.tiff;*.tif;*.bmp"),
            ("Tüm Dosyalar", "*.*")
        ]
        
        filepath = filedialog.askopenfilename(
            title="Dönüştürülecek dosyayı seçin",
            filetypes=filetypes
        )
        
        if filepath:
            self.file_var.set(filepath)
            base_name = os.path.splitext(os.path.basename(filepath))[0]
            default_output = f"{os.path.dirname(filepath)}/{base_name}_converted.docx"
            self.output_var.set(default_output)
    
    def select_output(self):
        filepath = filedialog.asksaveasfilename(
            title="Çıktı dosyasını seçin",
            defaultextension=".docx",
            filetypes=[("Word Dosyaları", "*.docx"), ("Tüm Dosyalar", "*.*")]
        )
        
        if filepath:
            self.output_var.set(filepath)
    
    def convert(self):
        input_path = self.file_var.get()
        output_path = self.output_var.get()
        
        if not input_path:
            messagebox.showerror("Hata", "Lütfen dönüştürülecek dosyayı seçin")
            return
        
        if not output_path:
            messagebox.showerror("Hata", "Lütfen çıktı dosyasını belirtin")
            return
        
        # İş parçacığında dönüştürme işlemi
        self.progress.start()
        self.status_var.set("Dönüştürülüyor...")
        
        def process():
            try:
                self.converter.convert(input_path, output_path)
                self.root.after(0, lambda: self.conversion_complete(output_path))
            except Exception as e:
                self.root.after(0, lambda: self.conversion_error(str(e)))
        
        threading.Thread(target=process, daemon=True).start()
    
    def conversion_complete(self, output_path):
        self.progress.stop()
        self.status_var.set("Dönüştürme tamamlandı")
        messagebox.showinfo("Başarılı", f"Dönüştürme tamamlandı!\n\nDosya kaydedildi: {output_path}")
    
    def conversion_error(self, error_message):
        self.progress.stop()
        self.status_var.set("Hata oluştu")
        messagebox.showerror("Hata", f"Dönüştürme sırasında bir hata oluştu:\n{error_message}")

def main():
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 