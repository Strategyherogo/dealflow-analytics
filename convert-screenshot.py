#!/usr/bin/env python3
"""
Convert and optimize screenshots for Chrome Web Store
Required sizes: 1280x800 or 640x400
"""

from PIL import Image
import os
import sys

def convert_screenshot(input_path, output_dir="chrome-store-screenshots"):
    """Convert screenshot to Chrome Web Store specifications"""
    
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the image
    try:
        img = Image.open(input_path)
        print(f"Original size: {img.size}")
    except Exception as e:
        print(f"Error opening image: {e}")
        return
    
    # Chrome Web Store recommended size
    target_sizes = [
        (1280, 800, "large"),
        (640, 400, "small")
    ]
    
    for width, height, size_name in target_sizes:
        # Create a new image with the target size
        new_img = Image.new('RGB', (width, height), color='white')
        
        # Calculate scaling to fit the image
        img_ratio = img.width / img.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            # Image is wider - fit by width
            new_width = width
            new_height = int(width / img_ratio)
        else:
            # Image is taller - fit by height
            new_height = height
            new_width = int(height * img_ratio)
        
        # Resize the image
        resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate position to center the image
        x = (width - new_width) // 2
        y = (height - new_height) // 2
        
        # Paste the resized image onto the new canvas
        new_img.paste(resized, (x, y))
        
        # Save the image
        filename = f"screenshot_{size_name}_{width}x{height}.png"
        output_path = os.path.join(output_dir, filename)
        new_img.save(output_path, 'PNG', optimize=True)
        print(f"✅ Saved: {output_path}")
    
    # Also save a cropped version that fills the frame
    for width, height, size_name in target_sizes:
        # Calculate crop dimensions
        img_ratio = img.width / img.height
        target_ratio = width / height
        
        if img_ratio > target_ratio:
            # Image is wider - crop sides
            new_height = img.height
            new_width = int(img.height * target_ratio)
            left = (img.width - new_width) // 2
            top = 0
        else:
            # Image is taller - crop top/bottom
            new_width = img.width
            new_height = int(img.width / target_ratio)
            left = 0
            top = (img.height - new_height) // 2
        
        # Crop the image
        cropped = img.crop((left, top, left + new_width, top + new_height))
        
        # Resize to exact dimensions
        final = cropped.resize((width, height), Image.Resampling.LANCZOS)
        
        # Save the cropped version
        filename = f"screenshot_{size_name}_cropped_{width}x{height}.png"
        output_path = os.path.join(output_dir, filename)
        final.save(output_path, 'PNG', optimize=True)
        print(f"✅ Saved cropped: {output_path}")

def create_promotional_images():
    """Create promotional tile templates"""
    sizes = [
        (440, 280, "small_tile"),
        (920, 680, "large_tile"),
        (1400, 560, "marquee")
    ]
    
    output_dir = "chrome-store-screenshots"
    
    for width, height, name in sizes:
        # Create a gradient background
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        
        # Save template
        filename = f"template_{name}_{width}x{height}.png"
        output_path = os.path.join(output_dir, filename)
        img.save(output_path, 'PNG')
        print(f"📋 Template created: {output_path}")

if __name__ == "__main__":
    print("🖼️  Chrome Web Store Screenshot Converter")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        convert_screenshot(input_file)
    else:
        print("\nUsage: python3 convert-screenshot.py <screenshot.png>")
        print("\nCreating promotional templates...")
        create_promotional_images()
        print("\n📌 Tip: Save your screenshot and run:")
        print("   python3 convert-screenshot.py your-screenshot.png")