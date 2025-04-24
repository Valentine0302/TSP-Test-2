import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageOps

# Estonian flag colors
ESTONIAN_BLUE = (0, 114, 206)  # RGB
ESTONIAN_BLACK = (0, 0, 0)     # RGB
ESTONIAN_WHITE = (255, 255, 255)  # RGB

def create_multimodal_transport_image():
    """Create an illustration for multimodal transport in Anton Pieck style with Estonian flag colors"""
    # Create a blank canvas with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), ESTONIAN_WHITE)
    draw = ImageDraw.Draw(image)
    
    # Draw a vintage port scene with ships, trains and trucks
    
    # Background - sky and water
    for y in range(height):
        # Sky gradient (lighter to darker blue)
        if y < height // 3:
            blue_value = max(ESTONIAN_BLUE[2] - y // 2, 100)
            draw.line([(0, y), (width, y)], fill=(ESTONIAN_BLUE[0], ESTONIAN_BLUE[1], blue_value))
        # Water (darker blue)
        elif y > height // 2:
            blue_value = max(ESTONIAN_BLUE[2] - 50, 50)
            draw.line([(0, y), (width, y)], fill=(ESTONIAN_BLUE[0], ESTONIAN_BLUE[1], blue_value))
    
    # Draw port/dock (black)
    draw.rectangle([(50, height//2), (width-50, height//2+30)], fill=ESTONIAN_BLACK)
    
    # Draw vintage ship (blue and black)
    ship_x = 200
    ship_y = height//2 + 100
    # Ship hull
    draw.polygon([(ship_x, ship_y), (ship_x+200, ship_y), (ship_x+180, ship_y+80), (ship_x+20, ship_y+80)], 
                fill=ESTONIAN_BLUE)
    # Ship cabin
    draw.rectangle([(ship_x+50, ship_y-40), (ship_x+150, ship_y)], fill=ESTONIAN_BLACK)
    # Ship smokestack
    draw.rectangle([(ship_x+100, ship_y-80), (ship_x+120, ship_y-40)], fill=ESTONIAN_BLACK)
    draw.ellipse([(ship_x+95, ship_y-90), (ship_x+125, ship_y-80)], fill=ESTONIAN_BLACK)
    
    # Draw vintage train (black with blue accents)
    train_x = 500
    train_y = height//2 - 20
    # Train body
    draw.rectangle([(train_x, train_y-30), (train_x+150, train_y)], fill=ESTONIAN_BLACK)
    # Train cabin
    draw.rectangle([(train_x+150, train_y-50), (train_x+200, train_y)], fill=ESTONIAN_BLACK)
    # Train wheels
    for wheel_x in [train_x+30, train_x+70, train_x+110, train_x+170]:
        draw.ellipse([(wheel_x, train_y), (wheel_x+20, train_y+20)], fill=ESTONIAN_BLACK, outline=ESTONIAN_BLUE)
    # Train smokestack
    draw.rectangle([(train_x+180, train_y-70), (train_x+190, train_y-50)], fill=ESTONIAN_BLACK)
    
    # Draw vintage truck (blue with black accents)
    truck_x = 100
    truck_y = height//2 - 20
    # Truck body
    draw.rectangle([(truck_x, truck_y-30), (truck_x+80, truck_y)], fill=ESTONIAN_BLUE)
    # Truck cabin
    draw.rectangle([(truck_x-40, truck_y-40), (truck_x, truck_y)], fill=ESTONIAN_BLUE)
    # Truck wheels
    draw.ellipse([(truck_x-30, truck_y), (truck_x-10, truck_y+20)], fill=ESTONIAN_BLACK)
    draw.ellipse([(truck_x+20, truck_y), (truck_x+40, truck_y+20)], fill=ESTONIAN_BLACK)
    draw.ellipse([(truck_x+60, truck_y), (truck_x+80, truck_y+20)], fill=ESTONIAN_BLACK)
    
    # Add Anton Pieck style details - fine lines and textures
    # Apply a slight sepia tone for vintage feel
    image = ImageOps.colorize(ImageOps.grayscale(image), ESTONIAN_WHITE, ESTONIAN_BLUE)
    
    # Add some noise/grain for vintage effect
    noise = Image.effect_noise((width, height), 10)
    noise = noise.convert('RGB')
    image = Image.blend(image, noise, 0.1)
    
    # Apply a slight blur for soft edges (Anton Pieck style)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    return image

def create_europe_transport_image():
    """Create an illustration for Europe transport in Anton Pieck style with Estonian flag colors"""
    # Create a blank canvas with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), ESTONIAN_WHITE)
    draw = ImageDraw.Draw(image)
    
    # Draw a European cityscape with vintage trucks and trains
    
    # Background - sky
    for y in range(height // 3):
        # Sky gradient (lighter to darker blue)
        blue_value = max(ESTONIAN_BLUE[2] - y // 2, 100)
        draw.line([(0, y), (width, y)], fill=(ESTONIAN_BLUE[0], ESTONIAN_BLUE[1], blue_value))
    
    # Draw European cityscape silhouette (black)
    # Cathedral/church with spires
    draw.polygon([(100, height//3), (150, height//3-100), (200, height//3)], fill=ESTONIAN_BLACK)
    # Buildings
    for x in range(250, width-100, 100):
        height_var = np.random.randint(50, 120)
        draw.rectangle([(x, height//3-height_var), (x+70, height//3)], fill=ESTONIAN_BLACK)
        # Windows
        for wy in range(height//3-height_var+10, height//3-10, 15):
            for wx in range(x+10, x+70-10, 15):
                draw.rectangle([(wx, wy), (wx+7, wy+10)], fill=ESTONIAN_BLUE)
    
    # Draw road (black)
    draw.rectangle([(0, height//2), (width, height//2+50)], fill=ESTONIAN_BLACK)
    # Road markings (white)
    for x in range(0, width, 50):
        draw.rectangle([(x, height//2+20), (x+30, height//2+30)], fill=ESTONIAN_WHITE)
    
    # Draw vintage European truck (blue with black accents)
    truck_x = 300
    truck_y = height//2
    # Truck body - more European style
    draw.rectangle([(truck_x, truck_y-40), (truck_x+120, truck_y)], fill=ESTONIAN_BLUE)
    # Truck cabin - rounded European style
    draw.rectangle([(truck_x-50, truck_y-50), (truck_x, truck_y)], fill=ESTONIAN_BLUE)
    draw.arc([(truck_x-70, truck_y-70), (truck_x-30, truck_y-30)], 90, 180, fill=ESTONIAN_BLUE, width=5)
    # Truck wheels
    draw.ellipse([(truck_x-40, truck_y), (truck_x-20, truck_y+20)], fill=ESTONIAN_BLACK)
    draw.ellipse([(truck_x+20, truck_y), (truck_x+40, truck_y+20)], fill=ESTONIAN_BLACK)
    draw.ellipse([(truck_x+80, truck_y), (truck_x+100, truck_y+20)], fill=ESTONIAN_BLACK)
    
    # Draw vintage European train (black with blue accents)
    train_x = 100
    train_y = height//2 + 100
    # Train tracks
    draw.rectangle([(0, train_y+30), (width, train_y+35)], fill=ESTONIAN_BLACK)
    for x in range(0, width, 20):
        draw.rectangle([(x, train_y+20), (x+5, train_y+45)], fill=ESTONIAN_BLACK)
    # Train body - European style locomotive
    draw.rectangle([(train_x, train_y-30), (train_x+150, train_y+30)], fill=ESTONIAN_BLACK)
    # Train cabin
    draw.rectangle([(train_x+150, train_y-50), (train_x+200, train_y+30)], fill=ESTONIAN_BLACK)
    # Train wheels
    for wheel_x in [train_x+30, train_x+70, train_x+110, train_x+170]:
        draw.ellipse([(wheel_x, train_y+10), (wheel_x+30, train_y+40)], fill=ESTONIAN_BLACK, outline=ESTONIAN_BLUE)
    # Train smokestack
    draw.rectangle([(train_x+180, train_y-80), (train_x+195, train_y-50)], fill=ESTONIAN_BLACK)
    # Steam
    draw.ellipse([(train_x+170, train_y-100), (train_x+210, train_y-70)], fill=ESTONIAN_WHITE, outline=None)
    draw.ellipse([(train_x+190, train_y-120), (train_x+240, train_y-80)], fill=ESTONIAN_WHITE, outline=None)
    
    # Add Anton Pieck style details - fine lines and textures
    # Apply a slight sepia tone for vintage feel
    image = ImageOps.colorize(ImageOps.grayscale(image), ESTONIAN_WHITE, ESTONIAN_BLUE)
    
    # Add some noise/grain for vintage effect
    noise = Image.effect_noise((width, height), 10)
    noise = noise.convert('RGB')
    image = Image.blend(image, noise, 0.1)
    
    # Apply a slight blur for soft edges (Anton Pieck style)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    return image

def create_asia_transport_image():
    """Create an illustration for Central Asia transport in Anton Pieck style with Estonian flag colors"""
    # Create a blank canvas with white background
    width, height = 800, 600
    image = Image.new('RGB', (width, height), ESTONIAN_WHITE)
    draw = ImageDraw.Draw(image)
    
    # Draw a Central Asian landscape with mountains, Silk Road and caravans
    
    # Background - sky
    for y in range(height // 3):
        # Sky gradient (lighter to darker blue)
        blue_value = max(ESTONIAN_BLUE[2] - y // 2, 100)
        draw.line([(0, y), (width, y)], fill=(ESTONIAN_BLUE[0], ESTONIAN_BLUE[1], blue_value))
    
    # Draw mountains (blue and black)
    # Far mountains (blue)
    points = [(0, height//3), (100, height//4), (200, height//3-20), 
              (300, height//4+30), (400, height//3-50), (500, height//4+10),
              (600, height//3-30), (700, height//4+50), (width, height//3),
              (width, height//3), (0, height//3)]
    draw.polygon(points, fill=ESTONIAN_BLUE)
    
    # Near mountains (black)
    points = [(0, height//3+50), (150, height//3-30), (250, height//3+70), 
              (350, height//3), (450, height//3+100), (550, height//3-10),
              (650, height//3+50), (width, height//3+30),
              (width, height//2+50), (0, height//2+50)]
    draw.polygon(points, fill=ESTONIAN_BLACK)
    
    # Draw Silk Road (sandy path)
    draw.rectangle([(0, height//2+50), (width, height//2+100)], fill=ESTONIAN_WHITE)
    # Add some texture to the road
    for _ in range(1000):
        x = np.random.randint(0, width)
        y = np.random.randint(height//2+50, height//2+100)
        draw.point((x, y), fill=ESTONIAN_BLACK)
    
    # Draw caravan with camels and vintage trucks (blue and black)
    # Camels
    for x in range(100, 400, 100):
        # Camel body
        draw.ellipse([(x, height//2+20), (x+80, height//2+60)], fill=ESTONIAN_BLACK)
        # Camel neck and head
        draw.line([(x+70, height//2+30), (x+90, height//2)], fill=ESTONIAN_BLACK, width=10)
        draw.ellipse([(x+85, height//2-10), (x+100, height//2+10)], fill=ESTONIAN_BLACK)
        # Camel legs
        draw.line([(x+20, height//2+50), (x+20, height//2+90)], fill=ESTONIAN_BLACK, width=5)
        draw.line([(x+60, height//2+50), (x+60, height//2+90)], fill=ESTONIAN_BLACK, width=5)
    
    # Vintage Central Asian style truck
    truck_x = 500
    truck_y = height//2 + 50
    # Truck body
    draw.rectangle([(truck_x, truck_y-40), (truck_x+120, truck_y)], fill=ESTONIAN_BLUE)
    # Truck cabin
    draw.rectangle([(truck_x-50, truck_y-50), (truck_x, truck_y)], fill=ESTONIAN_BLUE)
    # Truck wheels
    draw.ellipse([(truck_x-40, truck_y), (truck_x-20, truck_y+20)], fill=ESTONIAN_BLACK)
    draw.ellipse([(truck_x+20, truck_y), (truck_x+40, truck_y+20)], fill=ESTONIAN_BLACK)
    draw.ellipse([(truck_x+80, truck_y), (truck_x+100, truck_y+20)], fill=ESTONIAN_BLACK)
    
    # Draw Central Asian style building/yurt
    yurt_x = 650
    yurt_y = height//2 + 30
    # Yurt dome
    draw.ellipse([(yurt_x, yurt_y-30), (yurt_x+100, yurt_y+30)], fill=ESTONIAN_WHITE, outline=ESTONIAN_BLACK)
    # Yurt base
    draw.rectangle([(yurt_x+10, yurt_y), (yurt_x+90, yurt_y+50)], fill=ESTONIAN_WHITE, outline=ESTONIAN_BLACK)
    # Yurt door
    draw.rectangle([(yurt_x+40, yurt_y+20), (yurt_x+60, yurt_y+50)], fill=ESTONIAN_BLUE)
    
    # Add Anton Pieck style details - fine lines and textures
    # Apply a slight sepia tone for vintage feel
    image = ImageOps.colorize(ImageOps.grayscale(image), ESTONIAN_WHITE, ESTONIAN_BLUE)
    
    # Add some noise/grain for vintage effect
    noise = Image.effect_noise((width, height), 10)
    noise = noise.convert('RGB')
    image = Image.blend(image, noise, 0.1)
    
    # Apply a slight blur for soft edges (Anton Pieck style)
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.2)
    
    return image

def main():
    # Create directory if it doesn't exist
    os.makedirs('/home/ubuntu/tsp_website/images/services_new', exist_ok=True)
    
    # Create and save multimodal transport image
    multimodal_image = create_multimodal_transport_image()
    multimodal_image.save('/home/ubuntu/tsp_website/images/services_new/multimodal_transport_anton_pieck.jpg')
    
    # Create and save Europe transport image
    europe_image = create_europe_transport_image()
    europe_image.save('/home/ubuntu/tsp_website/images/services_new/europe_transport_anton_pieck.jpg')
    
    # Create and save Asia transport image
    asia_image = create_asia_transport_image()
    asia_image.save('/home/ubuntu/tsp_website/images/services_new/asia_transport_anton_pieck.jpg')
    
    print("All images created successfully in Anton Pieck style with Estonian flag colors.")

if __name__ == "__main__":
    main()
