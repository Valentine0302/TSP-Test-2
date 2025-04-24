import os
import replicate
import requests
import time
from PIL import Image
from io import BytesIO

# Создаем директории для сохранения изображений
os.makedirs('/home/ubuntu/tsp_website/images/services/multimodal', exist_ok=True)
os.makedirs('/home/ubuntu/tsp_website/images/services/europe', exist_ok=True)
os.makedirs('/home/ubuntu/tsp_website/images/services/asia', exist_ok=True)

# Функция для генерации изображений с помощью Replicate API
def generate_anton_pieck_image(prompt, output_path):
    """
    Генерирует изображение в стиле Anton Pieck с использованием Replicate API
    
    Args:
        prompt (str): Текстовый запрос для генерации изображения
        output_path (str): Путь для сохранения изображения
    """
    try:
        # Используем модель Stable Diffusion XL
        output = replicate.run(
            "stability-ai/stable-diffusion-xl-base-1.0:7dc05c8abf3a3a1e53a54b7a6f7cc0f2f3a4b1f0a9e2e1e5e3e5e3e5e3e5e3e5",
            input={
                "prompt": prompt,
                "negative_prompt": "cartoon, 3d, low quality, blurry, distorted, deformed",
                "width": 1024,
                "height": 768,
                "num_outputs": 1,
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
                "scheduler": "K_EULER_ANCESTRAL"
            }
        )
        
        # Загружаем и сохраняем изображение
        if output and len(output) > 0:
            image_url = output[0]
            response = requests.get(image_url)
            if response.status_code == 200:
                img = Image.open(BytesIO(response.content))
                img.save(output_path)
                print(f"Изображение успешно сохранено: {output_path}")
                return True
            else:
                print(f"Ошибка при загрузке изображения: {response.status_code}")
        else:
            print("API не вернул URL изображения")
    except Exception as e:
        print(f"Ошибка при генерации изображения: {e}")
    
    return False

# Промпты для изображений в стиле Anton Pieck с цветами эстонского флага
prompts = {
    "multimodal": [
        "A detailed Anton Pieck style illustration of a port with ships, trains and trucks, using blue, black and white colors of Estonian flag, vintage detailed drawing, old European port scene with multiple transport modes, highly detailed pen and ink drawing with watercolor",
        "A detailed Anton Pieck style illustration of global transportation network with ships, planes and trucks in blue, black and white colors of Estonian flag, vintage detailed drawing, old world map with transport routes, highly detailed pen and ink drawing with watercolor",
        "A detailed Anton Pieck style illustration of container terminal with cranes loading containers between ships, trains and trucks, using blue, black and white colors of Estonian flag, vintage detailed drawing, busy port scene, highly detailed pen and ink drawing with watercolor"
    ],
    "europe": [
        "A detailed Anton Pieck style illustration of European trucks on a mountain road with old European architecture in background, using blue, black and white colors of Estonian flag, vintage detailed drawing, Alpine pass with transport, highly detailed pen and ink drawing with watercolor",
        "A detailed Anton Pieck style illustration of trucks crossing European borders with customs checkpoints, using blue, black and white colors of Estonian flag, vintage detailed drawing, old European border scene, highly detailed pen and ink drawing with watercolor",
        "A detailed Anton Pieck style illustration of trucks in an old European city square with historic buildings, using blue, black and white colors of Estonian flag, vintage detailed drawing, cobblestone streets, highly detailed pen and ink drawing with watercolor"
    ],
    "asia": [
        "A detailed Anton Pieck style illustration of trucks on the Silk Road with Central Asian mountains and camels, using blue, black and white colors of Estonian flag, vintage detailed drawing, ancient trade route scene, highly detailed pen and ink drawing with watercolor",
        "A detailed Anton Pieck style illustration of trucks at Central Asian border crossing with local architecture, using blue, black and white colors of Estonian flag, vintage detailed drawing, Kazakhstan border scene, highly detailed pen and ink drawing with watercolor",
        "A detailed Anton Pieck style illustration of trucks in Central Asian city with traditional architecture and bazaar, using blue, black and white colors of Estonian flag, vintage detailed drawing, Uzbekistan city scene, highly detailed pen and ink drawing with watercolor"
    ]
}

# Генерируем и сохраняем изображения
for service, service_prompts in prompts.items():
    for i, prompt in enumerate(service_prompts, 1):
        output_path = f"/home/ubuntu/tsp_website/images/services/{service}/{service}_variant{i}.jpeg"
        print(f"Генерация изображения для {service}, вариант {i}...")
        success = generate_anton_pieck_image(prompt, output_path)
        
        # Пауза между запросами, чтобы не перегружать API
        if success:
            time.sleep(5)
        else:
            print(f"Не удалось сгенерировать изображение для {service}, вариант {i}")

print("Генерация изображений завершена!")
