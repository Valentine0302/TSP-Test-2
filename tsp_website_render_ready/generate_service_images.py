import requests
from PIL import Image
import io
import os

# Create directories for storing the images
os.makedirs('/home/ubuntu/tsp_website/images/services', exist_ok=True)

# Define the service sections and their descriptions
services = [
    {
        "name": "multimodal_transport",
        "title": "Мультимодальные перевозки по всему миру",
        "description": "FTL/LTL, сборные грузы, генеральные грузы и негабаритные грузы",
        "prompts": [
            "Anton Pieck style illustration of multimodal transportation with ships, trucks and trains in blue, black and white colors of Estonian flag, vintage detailed drawing",
            "Anton Pieck style detailed drawing of global logistics network with cargo ships, trucks and trains in blue and black colors on white background, vintage illustration",
            "Vintage Anton Pieck style illustration of worldwide freight transportation with detailed ships, trucks and containers in Estonian flag colors (blue, black, white)"
        ]
    },
    {
        "name": "europe_transport",
        "title": "Автоперевозки по Европе любой сложности",
        "description": "FTL/LTL, негабаритные и тяжеловесные",
        "prompts": [
            "Anton Pieck style illustration of European truck transportation on winding roads through picturesque towns in blue, black and white colors, vintage detailed drawing",
            "Vintage Anton Pieck style drawing of heavy cargo transportation trucks on European highways in Estonian flag colors (blue, black, white), detailed illustration",
            "Anton Pieck style detailed illustration of freight trucks delivering cargo across European cities in blue and black colors on white background, vintage drawing"
        ]
    },
    {
        "name": "asia_transport",
        "title": "Перевозки грузов в Центральную Азию",
        "description": "Казахстан, Узбекистан, Таджикистан",
        "prompts": [
            "Anton Pieck style illustration of Silk Road transportation with trucks on Central Asian routes in blue, black and white colors of Estonian flag, vintage detailed drawing",
            "Vintage Anton Pieck style drawing of logistics transportation to Kazakhstan, Uzbekistan and Tajikistan in Estonian flag colors (blue, black, white), detailed illustration",
            "Anton Pieck style detailed illustration of freight delivery across Central Asian landscapes with mountains and desert roads in blue and black colors, vintage drawing"
        ]
    }
]

# Function to generate placeholder images with text
def create_placeholder_images(service):
    base_dir = '/home/ubuntu/tsp_website/images/services/'
    
    for i, prompt in enumerate(service["prompts"]):
        # Create a placeholder image with text
        img = Image.new('RGB', (800, 600), color=(240, 240, 240))
        
        # Save the image
        filename = f"{service['name']}_{i+1}.jpg"
        img.save(os.path.join(base_dir, filename))
        
        print(f"Created placeholder image: {filename}")
        print(f"Prompt that would be used: {prompt}")
    
    return [f"{service['name']}_{i+1}.jpg" for i in range(len(service["prompts"]))]

# Process each service
for service in services:
    print(f"\nProcessing service: {service['name']}")
    image_files = create_placeholder_images(service)
    service["image_files"] = image_files

print("\nPlaceholder images created successfully!")

# Save the service data for later use
import json
with open('/home/ubuntu/tsp_website/services_data.json', 'w', encoding='utf-8') as f:
    json.dump(services, f, ensure_ascii=False, indent=4)

print("Service data saved to services_data.json")
