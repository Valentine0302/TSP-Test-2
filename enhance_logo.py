import requests
from PIL import Image, ImageEnhance, ImageFilter
import io
import os

# Path to the original logo
original_logo_path = "/home/ubuntu/tsp_website/temp/original_logo.png"
output_dir = "/home/ubuntu/tsp_website/images/optimized"

# Load the original image
original_image = Image.open(original_logo_path)
print(f"Original image size: {original_image.size}")

# Create a higher resolution version (2x)
width, height = original_image.size
new_size = (width * 2, height * 2)
high_res_image = original_image.resize(new_size, Image.LANCZOS)
print(f"Resized image size: {high_res_image.size}")

# Apply enhancements
# 1. Sharpen the image
sharpened_image = high_res_image.filter(ImageFilter.SHARPEN)
sharpened_image = sharpened_image.filter(ImageFilter.SHARPEN)  # Apply twice for stronger effect

# 2. Increase contrast
enhancer = ImageEnhance.Contrast(sharpened_image)
contrast_image = enhancer.enhance(1.3)  # Increase contrast by 30%

# 3. Increase brightness slightly
enhancer = ImageEnhance.Brightness(contrast_image)
bright_image = enhancer.enhance(1.1)  # Increase brightness by 10%

# 4. Increase color saturation
enhancer = ImageEnhance.Color(bright_image)
final_image = enhancer.enhance(1.2)  # Increase color saturation by 20%

# Save the enhanced image
enhanced_logo_path = os.path.join(output_dir, "enhanced_logo.png")
final_image.save(enhanced_logo_path, "PNG")
print(f"Enhanced logo saved to: {enhanced_logo_path}")

# Create an SVG version for better scaling
svg_logo_path = os.path.join(output_dir, "logo.svg")
print(f"Original SVG path: {svg_logo_path}")

# Save the enhanced PNG as the main logo
final_image.save(os.path.join(output_dir, "logo.png"), "PNG")
print(f"Enhanced logo saved as main logo")

print("Logo enhancement completed successfully!")
