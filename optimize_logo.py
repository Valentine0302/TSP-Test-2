from PIL import Image, ImageEnhance
import os

# Пути к файлам
input_path = '/home/ubuntu/tsp_website/images/original_logo.png'
output_path = '/home/ubuntu/tsp_website/images/optimized/logo.png'
output_path_svg = '/home/ubuntu/tsp_website/images/optimized/logo.svg'

# Открываем изображение
img = Image.open(input_path)

# Увеличиваем размер (масштабируем в 2 раза)
width, height = img.size
new_size = (width * 2, height * 2)
img = img.resize(new_size, Image.LANCZOS)

# Улучшаем контрастность
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(1.2)

# Улучшаем резкость
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(1.5)

# Сохраняем улучшенное изображение
img.save(output_path, 'PNG', quality=95)

print(f"Логотип улучшен и сохранен в {output_path}")

# Создаем простой SVG файл на основе PNG для лучшего качества при масштабировании
# Это базовый SVG, который включает PNG как изображение
svg_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg width="{new_size[0]}" height="{new_size[1]}" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image width="{new_size[0]}" height="{new_size[1]}" xlink:href="logo.png"/>
</svg>'''

with open(output_path_svg, 'w') as f:
    f.write(svg_content)

print(f"SVG версия логотипа создана в {output_path_svg}")
