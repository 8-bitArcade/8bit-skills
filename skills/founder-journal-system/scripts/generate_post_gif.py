#!/usr/bin/env python3
"""Generate pixelated GIF signature for founder journal posts."""
import sys
import os
from PIL import Image, ImageDraw, ImageFont
import random

def generate_post_gif(post_number, output_path, width=200, height=200, palette=None):
    """Generate a pixelated GIF with post number as visual signature."""
    if palette is None:
        palette = [
            (0, 255, 127),   # Bright green
            (0, 200, 100),   # Darker green
            (0, 150, 75),    # Even darker
            (255, 255, 255), # White
            (50, 50, 50),    # Dark gray
        ]

    frames = []
    # Create 4 frames for animation
    for i in range(4):
        img = Image.new('RGB', (width, height), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw pixel grid
        pixel_size = 20
        for x in range(0, width, pixel_size):
            for y in range(0, height, pixel_size):
                # Create a pattern based on post number and frame
                if (x + y + i) % (post_number + 1) < 2:
                    color = palette[(x // pixel_size + y // pixel_size + i) % len(palette)]
                    draw.rectangle([x, y, x + pixel_size - 1, y + pixel_size - 1], fill=color)
                else:
                    draw.rectangle([x, y, x + pixel_size - 1, y + pixel_size - 1], fill=(0, 0, 0))
        
        # Draw post number in center
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Text position
        text = f"#{post_number}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        text_x = (width - text_w) // 2
        text_y = (height - text_h) // 2
        
        draw.rectangle([text_x - 5, text_y - 5, text_x + text_w + 5, text_y + text_h + 5], fill=(0, 0, 0))
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        
        frames.append(img)
    
    # Save as GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=200,
        loop=0
    )
    
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: generate_post_gif.py <post_number> <output_path>")
        sys.exit(1)
    
    post_num = int(sys.argv[1])
    output = sys.argv[2]
    
    result = generate_post_gif(post_num, output)
    print(f"Generated: {result}")
