import math, random
from PIL import Image, ImageDraw, ImageFilter

CANVAS = (1920, 1080)

def scalloped_cloud(cx, cy, w, h, seed, lobes=8, jitter=0.18):
    rnd = random.Random(seed)
    pts = []
    for i in range(lobes * 10):
        angle = (2 * math.pi * i) / (lobes * 10)
        lobe_wave = 1 + 0.055 * math.sin(angle * lobes)
        rx = (w / 2) * lobe_wave * (1 + rnd.uniform(-jitter * 0.08, jitter * 0.08))
        ry = (h / 2) * lobe_wave * (1 + rnd.uniform(-jitter * 0.08, jitter * 0.08))
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        pts.append((x, y))
    return pts

def make_bubble(out_name, w, h, seed, small_circles=True):
    pad = 60
    work_w, work_h = w + pad * 2, h + pad * 2
    cx, cy = work_w / 2, work_h / 2

    mask = Image.new("L", (work_w, work_h), 0)
    draw = ImageDraw.Draw(mask)
    poly = scalloped_cloud(cx, cy, w, h, seed)
    draw.polygon(poly, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(2.0))
    mask = mask.point(lambda p: 255 if p > 128 else 0)

    shadow_mask = mask.filter(ImageFilter.GaussianBlur(16))

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ox = (CANVAS[0] - work_w) // 2
    oy = (CANVAS[1] - work_h) // 2

    shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shadow_black = Image.new("RGBA", (work_w, work_h), (20, 15, 10, 150))
    shadow_layer = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    shadow_layer.paste(shadow_black, (0, 0), shadow_mask)
    shadow.paste(shadow_layer, (ox + 8, oy + 12), shadow_layer)
    canvas = Image.alpha_composite(canvas, shadow)

    cream = Image.new("RGBA", (work_w, work_h), (250, 246, 235, 255))
    fill = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    fill.paste(cream, (0, 0), mask)

    outline_mask = Image.new("L", (work_w, work_h), 0)
    ImageDraw.Draw(outline_mask).polygon(poly, outline=255, width=5)
    outline_mask = outline_mask.filter(ImageFilter.GaussianBlur(1.0))
    outline_layer = Image.new("RGBA", (work_w, work_h), (120, 105, 80, 255))
    fill.paste(outline_layer, (0, 0), outline_mask)

    fill_shifted = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    fill_shifted.paste(fill, (ox, oy), fill)
    canvas = Image.alpha_composite(canvas, fill_shifted)

    canvas.save(f"{out_name}.png")


make_bubble("bubble_shape_flagellants", 460, 320, seed=42)
make_bubble("bubble_shape_death", 380, 460, seed=43)
make_bubble("bubble_shape_danse", 420, 380, seed=44)
make_bubble("bubble_shape_witch", 440, 340, seed=45)

# small trailing thought-circles connecting head to bubble
trail = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
draw = ImageDraw.Draw(trail)
circles = [(0, 0, 26), (34, -46, 18), (58, -86, 11)]
ccx, ccy = CANVAS[0] // 2, CANVAS[1] // 2
for dx, dy, r in circles:
    x, y = ccx + dx, ccy + dy
    draw.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3], fill=(20, 15, 10, 140))
for dx, dy, r in circles:
    x, y = ccx + dx, ccy + dy
    draw.ellipse([x - r, y - r, x + r, y + r], fill=(250, 246, 235, 255))
    draw.ellipse([x - r, y - r, x + r, y + r], outline=(120, 105, 80, 255), width=3)
trail.save("bubble_trail.png")

print("done")
