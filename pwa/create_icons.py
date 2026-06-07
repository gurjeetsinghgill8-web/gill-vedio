"""
Quick icon creator — creates all PWA icon sizes
"""
import os, sys

try:
    from PIL import Image, ImageDraw, ImageFilter
except ImportError:
    os.system("pip install Pillow -q")
    from PIL import Image, ImageDraw, ImageFilter

SIZES = [72, 96, 128, 192, 512]
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "icons")
os.makedirs(OUTPUT_DIR, exist_ok=True)

for size in SIZES:
    img = Image.new("RGBA", (size, size), (10, 10, 15, 255))
    draw = ImageDraw.Draw(img)

    # Rounded purple background
    pad = size // 10
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=size // 5,
        fill=(124, 77, 255, 255)
    )

    # Film strip holes (top)
    hole_size = max(4, size // 18)
    hole_y = pad + hole_size
    for hx in range(pad + hole_size, size - pad - hole_size, hole_size * 3):
        draw.ellipse([hx, hole_y - hole_size//2, hx + hole_size, hole_y + hole_size//2],
                     fill=(10, 10, 15, 200))

    # Play triangle in center
    cx, cy = size // 2, size // 2 + pad // 2
    ts = size // 5
    draw.polygon([
        (cx - ts // 2, cy - ts),
        (cx - ts // 2, cy + ts),
        (cx + ts, cy)
    ], fill=(255, 255, 255, 255))

    # Cyan glow dot
    glow_r = size // 10
    draw.ellipse([
        cx + ts - glow_r, cy - glow_r,
        cx + ts + glow_r, cy + glow_r
    ], fill=(0, 229, 255, 180))

    output_path = os.path.join(OUTPUT_DIR, f"icon-{size}.png")
    img.save(output_path, "PNG")
    print(f"[OK] icon-{size}.png")

print("\n[DONE] All icons created in pwa/icons/")
