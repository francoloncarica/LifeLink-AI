"""Generate LifeLink AI PWA icons (run once after setup). Requires Pillow.

    python gen_icons.py
"""
from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parent / 'core' / 'static' / 'core'
OUT.mkdir(parents=True, exist_ok=True)

TEAL = (10, 185, 194)
BLUE = (10, 132, 255)
# Heartbeat pulse in a 24x24 viewBox (same path as the in-app logo).
PULSE = [(3, 12), (7, 12), (9, 17), (13, 4), (15, 12), (21, 12)]


def render(size):
    img = Image.new('RGB', (size, size), BLUE)
    px = img.load()
    for y in range(size):
        t = y / (size - 1)
        row = (
            int(TEAL[0] + (BLUE[0] - TEAL[0]) * t),
            int(TEAL[1] + (BLUE[1] - TEAL[1]) * t),
            int(TEAL[2] + (BLUE[2] - TEAL[2]) * t),
        )
        for x in range(size):
            px[x, y] = row

    d = ImageDraw.Draw(img)
    pad = size * 0.20
    scale = (size - 2 * pad) / 24.0
    pts = [(pad + x * scale, pad + y * scale) for x, y in PULSE]
    w = max(2, int(size * 0.055))
    d.line(pts, fill=(255, 255, 255), width=w, joint='curve')
    for p in (pts[0], pts[-1]):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=(255, 255, 255))
    return img


base = render(512)
base.save(OUT / 'icon-512.png')
base.resize((192, 192), Image.LANCZOS).save(OUT / 'icon-192.png')
base.resize((180, 180), Image.LANCZOS).save(OUT / 'apple-touch-icon.png')
print('PWA icons generated in', OUT)
