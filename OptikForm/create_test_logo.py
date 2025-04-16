from PIL import Image

# Yeşil renkli test logosu oluştur
img = Image.new('RGBA', (300, 100), color=(0, 155, 0, 255))
img.save('test_logo.png')

print("Test logo başarıyla oluşturuldu: test_logo.png") 