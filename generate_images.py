import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

# Создаем директорию для изображений, если она не существует
os.makedirs('/home/ubuntu/tsp_website/images/services', exist_ok=True)

# Цвета эстонского флага
ESTONIAN_BLUE = (0, 114, 206)  # Синий
ESTONIAN_BLACK = (0, 0, 0)     # Черный
ESTONIAN_WHITE = (255, 255, 255)  # Белый

def create_stylized_image(filename, title, style="transport"):
    """Создает стилизованное изображение в стиле Anton Pieck с цветами эстонского флага"""
    width, height = 800, 500
    img = Image.new('RGB', (width, height), ESTONIAN_WHITE)
    draw = ImageDraw.Draw(img)
    
    # Создаем фон с градиентом
    for y in range(height):
        for x in range(width):
            # Создаем эффект старой бумаги
            noise = np.random.randint(0, 15)
            shade = 245 - noise
            img.putpixel((x, y), (shade, shade, shade - 5))
    
    # Добавляем текстуру
    for _ in range(5000):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(1, 4)
        shade = np.random.randint(180, 220)
        draw.ellipse((x, y, x+size, y+size), fill=(shade, shade, shade))
    
    # Рисуем рамку
    border_width = 20
    draw.rectangle(
        [(border_width, border_width), (width-border_width, height-border_width)],
        outline=ESTONIAN_BLUE,
        width=3
    )
    
    # Добавляем элементы в зависимости от стиля
    if style == "multimodal":
        # Рисуем корабль
        ship_color = ESTONIAN_BLUE
        ship_x, ship_y = width//4, height//2
        draw.polygon(
            [(ship_x, ship_y), (ship_x + 150, ship_y), (ship_x + 180, ship_y - 50), 
             (ship_x - 30, ship_y - 50)],
            fill=ship_color,
            outline=ESTONIAN_BLACK
        )
        # Мачта
        draw.line([(ship_x + 75, ship_y - 50), (ship_x + 75, ship_y - 150)], 
                 fill=ESTONIAN_BLACK, width=3)
        # Флаг
        draw.rectangle([(ship_x + 75, ship_y - 150), (ship_x + 125, ship_y - 120)],
                      fill=ESTONIAN_BLUE, outline=ESTONIAN_BLACK)
        
        # Рисуем поезд
        train_x, train_y = width//2 + 100, height//2 + 100
        # Исправляем координаты, чтобы y1 >= y0
        draw.rectangle([(train_x, train_y - 50), (train_x + 100, train_y)],
                      fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
        # Колеса
        draw.ellipse([(train_x + 10, train_y), (train_x + 30, train_y + 20)],
                    fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
        draw.ellipse([(train_x + 70, train_y), (train_x + 90, train_y + 20)],
                    fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
        
    elif style == "europe":
        # Рисуем дорогу
        road_y = height//2 + 50
        draw.rectangle([(0, road_y), (width, road_y + 50)],
                      fill=(100, 100, 100), outline=ESTONIAN_BLACK)
        # Разметка
        for i in range(10):
            x = i * width//10
            draw.rectangle([(x, road_y + 20), (x + width//20, road_y + 30)],
                          fill=ESTONIAN_WHITE)
        
        # Рисуем грузовик
        truck_x, truck_y = width//3, road_y - 30
        # Кабина - исправляем координаты
        draw.rectangle([(truck_x, truck_y - 70), (truck_x + 80, truck_y)],
                      fill=ESTONIAN_BLUE, outline=ESTONIAN_BLACK, width=2)
        # Кузов - исправляем координаты
        draw.rectangle([(truck_x + 80, truck_y - 100), (truck_x + 200, truck_y)],
                      fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK, width=2)
        # Колеса
        draw.ellipse([(truck_x + 30, truck_y), (truck_x + 60, truck_y + 30)],
                    fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
        draw.ellipse([(truck_x + 120, truck_y), (truck_x + 150, truck_y + 30)],
                    fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
        draw.ellipse([(truck_x + 170, truck_y), (truck_x + 200, truck_y + 30)],
                    fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
        
    elif style == "asia":
        # Рисуем горы
        for i in range(3):
            peak_x = width//4 + i * width//4
            peak_y = height//4
            draw.polygon(
                [(peak_x - 100, height//2), (peak_x, peak_y), (peak_x + 100, height//2)],
                fill=(150, 150, 150),
                outline=ESTONIAN_BLACK
            )
            # Снег на вершинах
            draw.polygon(
                [(peak_x - 30, peak_y + 30), (peak_x, peak_y), (peak_x + 30, peak_y + 30)],
                fill=ESTONIAN_WHITE,
                outline=ESTONIAN_BLACK
            )
        
        # Рисуем караван грузовиков
        for i in range(3):
            truck_x = width//6 + i * width//4
            truck_y = height//2 + 50
            # Кабина - исправляем координаты
            draw.rectangle([(truck_x, truck_y - 30), (truck_x + 40, truck_y)],
                          fill=ESTONIAN_BLUE, outline=ESTONIAN_BLACK, width=1)
            # Кузов - исправляем координаты
            draw.rectangle([(truck_x + 40, truck_y - 50), (truck_x + 100, truck_y)],
                          fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK, width=1)
            # Колеса
            draw.ellipse([(truck_x + 15, truck_y), (truck_x + 30, truck_y + 15)],
                        fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
            draw.ellipse([(truck_x + 60, truck_y), (truck_x + 75, truck_y + 15)],
                        fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
            draw.ellipse([(truck_x + 85, truck_y), (truck_x + 100, truck_y + 15)],
                        fill=ESTONIAN_BLACK, outline=ESTONIAN_BLACK)
    
    # Добавляем название в верхней части
    title_y = 50
    # Тень для текста
    draw.text((width//2 - 98, title_y + 2), title, fill=ESTONIAN_BLACK)
    # Основной текст
    draw.text((width//2 - 100, title_y), title, fill=ESTONIAN_BLUE)
    
    # Применяем фильтр для эффекта акварели
    img = img.filter(ImageFilter.SMOOTH)
    
    # Сохраняем изображение
    img.save(filename)
    print(f"Создано изображение: {filename}")
    return filename

# Создаем изображения для мультимодальных перевозок
create_stylized_image('/home/ubuntu/tsp_website/images/services/multimodal_transport_1.jpg', 
                     "Мультимодальные перевозки", "multimodal")
create_stylized_image('/home/ubuntu/tsp_website/images/services/multimodal_transport_2.jpg', 
                     "Мультимодальные перевозки", "multimodal")
create_stylized_image('/home/ubuntu/tsp_website/images/services/multimodal_transport_3.jpg', 
                     "Мультимодальные перевозки", "multimodal")

# Создаем изображения для перевозок по Европе
create_stylized_image('/home/ubuntu/tsp_website/images/services/europe_transport_1.jpg', 
                     "Перевозки по Европе", "europe")
create_stylized_image('/home/ubuntu/tsp_website/images/services/europe_transport_2.jpg', 
                     "Перевозки по Европе", "europe")
create_stylized_image('/home/ubuntu/tsp_website/images/services/europe_transport_3.jpg', 
                     "Перевозки по Европе", "europe")

# Создаем изображения для перевозок в Центральную Азию
create_stylized_image('/home/ubuntu/tsp_website/images/services/asia_transport_1.jpg', 
                     "Перевозки в Центральную Азию", "asia")
create_stylized_image('/home/ubuntu/tsp_website/images/services/asia_transport_2.jpg', 
                     "Перевозки в Центральную Азию", "asia")
create_stylized_image('/home/ubuntu/tsp_website/images/services/asia_transport_3.jpg', 
                     "Перевозки в Центральную Азию", "asia")

print("Все изображения успешно созданы!")
