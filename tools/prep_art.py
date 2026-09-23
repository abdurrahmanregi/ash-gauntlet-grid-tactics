"""Turn generated pictures into sprites with a clear edge."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = Path(
    r"C:\Users\abdur\.grok\sessions\C%3A%5CUsers%5Cabdur%5COneDrive%5CPersonal%5Cisometric-grid-tactics-game"
    r"\01a0cd84-ed49-7fb0-a41b-662d186bafc8\images"
)

MAPPING = {
    "5.jpg": ("sprites/kairo.png", 128),
    "4.jpg": ("sprites/shio.png", 116),
    "12.jpg": ("sprites/sword_two.png", 124),
    "14.jpg": ("sprites/spear_one.png", 132),
    "13.jpg": ("sprites/swallow.png", 116),
    "1.jpg": ("sprites/pawn.png", 120),
    "15.jpg": ("sprites/bushi.png", 132),
    "8.jpg": ("props/tree.png", 120),
    "9.jpg": ("props/house.png", 120),
    "11.jpg": ("props/gauntlet.png", 96),
    "2.jpg": ("fx/issen.png", 84),
}


def is_pink(r: int, g: int, b: int) -> bool:
    return r > 120 and b > 90 and g < 155 and (r - g) > 30 and (b - g) > 18 and r + 30 > b


def key_image(image: Image.Image) -> Image.Image:
    image = image.convert("RGBA")
    pixels = image.load()
    width, height = image.size
    corners = [
        pixels[0, 0],
        pixels[width - 1, 0],
        pixels[0, height - 1],
        pixels[width - 1, height - 1],
    ]
    ref = tuple(sum(px[i] for px in corners) // 4 for i in range(3))
    seen = [[False] * width for _ in range(height)]
    stack = []
    for x in range(width):
        stack.append((x, 0))
        stack.append((x, height - 1))
    for y in range(height):
        stack.append((0, y))
        stack.append((width - 1, y))

    def background(r: int, g: int, b: int) -> bool:
        if is_pink(r, g, b):
            near = abs(r - ref[0]) + abs(g - ref[1]) + abs(b - ref[2]) < 150
            return near or (r > 150 and b > 100 and g < 120)
        return False

    while stack:
        x, y = stack.pop()
        if x < 0 or y < 0 or x >= width or y >= height or seen[y][x]:
            continue
        seen[y][x] = True
        r, g, b, a = pixels[x, y]
        if a == 0 or background(r, g, b):
            pixels[x, y] = (r, g, b, 0)
            stack.extend(((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)))
    for _ in range(4):
        wipe = []
        for y in range(height):
            for x in range(width):
                r, g, b, a = pixels[x, y]
                if a == 0 or not is_pink(r, g, b):
                    continue
                neighbors = 0
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if nx < 0 or ny < 0 or nx >= width or ny >= height or pixels[nx, ny][3] == 0:
                        neighbors += 1
                if neighbors >= 2:
                    wipe.append((x, y))
        for x, y in wipe:
            r, g, b, _a = pixels[x, y]
            pixels[x, y] = (r, g, b, 0)
    bbox = image.getbbox()
    if bbox:
        image = image.crop(bbox)
    return image


def fit(image: Image.Image, height: int) -> Image.Image:
    scale = height / image.height
    size = (max(1, int(image.width * scale)), height)
    return image.resize(size, Image.Resampling.LANCZOS)


def main() -> None:
    out_root = ROOT / "assets"
    for source_name, (dest_name, height) in MAPPING.items():
        source = SRC / source_name
        if not source.exists():
            print("missing", source_name)
            continue
        raw = Image.open(source).convert("RGBA")
        corner = raw.getpixel((0, 0))
        image = fit(key_image(raw), height)
        clear = sum(1 for px in image.getdata() if px[3] == 0)
        dest = out_root / dest_name
        dest.parent.mkdir(parents=True, exist_ok=True)
        image.save(dest)
        print(dest_name, image.size, "clear", round(clear / max(1, image.width * image.height), 2), "corner", corner)


if __name__ == "__main__":
    main()
