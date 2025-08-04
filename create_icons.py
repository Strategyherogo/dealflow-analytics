#!/usr/bin/env python3
"""
Create simple icons for DealFlow Analytics Chrome extension
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_icon(size):
    """Create a simple icon with the specified size"""
    # Create a new image with a gradient background
    img = Image.new('RGB', (size, size), color='#4361ee')
    draw = ImageDraw.Draw(img)
    
    # Add a simple design - circle with "DF" text
    margin = size // 8
    draw.ellipse(
        [margin, margin, size - margin, size - margin],
        fill='#ffffff',
        outline='#3f37c9',
        width=max(1, size // 32)
    )
    
    # Add text "DF" (DealFlow) - simplified version
    text = "DF"
    # Use default font for simplicity
    font = ImageFont.load_default()
    
    # For very small sizes, use a simpler design
    if size <= 16:
        # Just draw a small filled circle
        draw.ellipse(
            [size//4, size//4, 3*size//4, 3*size//4],
            fill='#4361ee'
        )
    else:
        # Draw text for larger sizes
        # Approximate text positioning
        text_x = size // 3
        text_y = size // 3
        draw.text((text_x, text_y), text, fill='#4361ee', font=font)
    
    return img

def main():
    """Create all required icon sizes"""
    sizes = [16, 32, 48, 128]
    icons_dir = "extension/icons"
    
    print("Creating DealFlow Analytics icons...")
    
    for size in sizes:
        icon = create_icon(size)
        filepath = os.path.join(icons_dir, f"icon{size}.png")
        icon.save(filepath)
        print(f"✓ Created {filepath}")
    
    print("\nIcons created successfully!")

if __name__ == "__main__":
    main()