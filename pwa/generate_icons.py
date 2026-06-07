"""
GILL VEDIO PWA — Icon Generator
Run this script to generate all required icon sizes from the source icon
Requirements: pip install Pillow
"""

from PIL import Image
import os

SOURCE = "gill_vedio_icon_1780843262458.png"  # Replace with actual icon file
SIZES = [72, 96, 128, 192, 512]
OUTPUT_DIR = "icons"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Try to open source icon
try:
    img = Image.open(SOURCE).convert("RGBA")
    for size in SIZES:
        resized = img.resize((size, size), Image.LANCZOS)
        output_path = os.path.join(OUTPUT_DIR, f"icon-{size}.png")
        resized.save(output_path, "PNG")
        print(f"✓ Created {output_path}")
    print("\n✅ All icons generated!")
except FileNotFoundError:
    # Create placeholder icons with gradient
    print("Source icon not found. Creating placeholder icons...")
    from PIL import ImageDraw

    for size in SIZES:
        img = Image.new("RGBA", (size, size), (10, 10, 15, 255))
        draw = ImageDraw.Draw(img)

        # Draw a simple film icon
        padding = size // 6
        # Purple background rectangle
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=size // 8,
            fill=(124, 77, 255, 255)
        )
        # White play triangle
        cx, cy = size // 2, size // 2
        tri_size = size // 5
        draw.polygon([
            (cx - tri_size // 2, cy - tri_size),
            (cx - tri_size // 2, cy + tri_size),
            (cx + tri_size, cy)
        ], fill=(255, 255, 255, 255))

        output_path = os.path.join(OUTPUT_DIR, f"icon-{size}.png")
        img.save(output_path, "PNG")
        print(f"✓ Created placeholder {output_path}")

    print("\n✅ Placeholder icons created!")
    print("Replace with your actual icon by running with your icon file.")
