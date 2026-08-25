import random, math
from PIL import Image, ImageDraw, ImageFilter

CANVAS = (1920, 1080)

def torn_polygon(cx, cy, w, h, seed, jitter=0.06, points=24):
    rnd = random.Random(seed)
    pts = []
    for i in range(points):
        angle = (2 * math.pi * i) / points
        rx = (w / 2) * (1 + rnd.uniform(-jitter, jitter))
        ry = (h / 2) * (1 + rnd.uniform(-jitter, jitter))
        x = cx + rx * math.cos(angle)
        y = cy + ry * math.sin(angle)
        pts.append((x, y))
    return pts

def make_torn_piece(image_path, out_name, piece_w, piece_h, seed, border=26):
    img = Image.open(image_path).convert("RGB")
    src_ratio = img.width / img.height
    dst_ratio = piece_w / piece_h
    if src_ratio > dst_ratio:
        new_h = img.height
        new_w = int(new_h * dst_ratio)
        x0 = (img.width - new_w) // 2
        img = img.crop((x0, 0, x0 + new_w, new_h))
    else:
        new_w = img.width
        new_h = int(new_w / dst_ratio)
        y0 = (img.height - new_h) // 2
        img = img.crop((0, y0, new_w, y0 + new_h))
    img = img.resize((piece_w, piece_h), Image.LANCZOS)

    pad = 40
    work_w, work_h = piece_w + pad * 2, piece_h + pad * 2
    cx, cy = work_w / 2, work_h / 2

    mask = Image.new("L", (work_w, work_h), 0)
    draw = ImageDraw.Draw(mask)
    poly = torn_polygon(cx, cy, piece_w - border, piece_h - border, seed)
    draw.polygon(poly, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(1.2))
    mask = mask.point(lambda p: 255 if p > 128 else 0)

    photo_canvas = Image.new("RGB", (work_w, work_h), (0, 0, 0))
    photo_canvas.paste(img, (pad, pad))

    piece_rgba = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    piece_rgba.paste(photo_canvas, (0, 0), mask)

    edge = Image.new("L", (work_w, work_h), 0)
    ImageDraw.Draw(edge).polygon(poly, outline=255, width=6)
    edge = edge.filter(ImageFilter.GaussianBlur(1.5))
    cream_layer = Image.new("RGBA", (work_w, work_h), (250, 246, 235, 255))
    piece_rgba = Image.composite(cream_layer, piece_rgba, Image.eval(edge, lambda p: int(p * 0.35)))

    shadow_mask = mask.filter(ImageFilter.GaussianBlur(14))
    shadow = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    shadow_black = Image.new("RGBA", (work_w, work_h), (20, 15, 10, 160))
    shadow.paste(shadow_black, (0, 0), shadow_mask)

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ox = (CANVAS[0] - work_w) // 2
    oy = (CANVAS[1] - work_h) // 2
    shadow_shifted = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shadow_shifted.paste(shadow, (ox + 10, oy + 14), shadow)
    canvas = Image.alpha_composite(canvas, shadow_shifted)
    piece_shifted = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    piece_shifted.paste(piece_rgba, (ox, oy), piece_rgba)
    canvas = Image.alpha_composite(canvas, piece_shifted)

    canvas.save(f"{out_name}.png")


# Hero piece — larger, portrait orientation, main subject
make_torn_piece("hero_zeitungsleser.jpg", "piece_hero", 560, 760, seed=10)

# Thought-bubble contents — smaller pieces
make_torn_piece("goya_flagellants.jpg", "piece_bubble_flagellants", 380, 260, seed=1)
make_torn_piece("poncher_death.jpg", "piece_bubble_death", 300, 380, seed=2)
make_torn_piece("piece_danse_macabre.jpg", "piece_bubble_danse", 340, 300, seed=5)
make_torn_piece("piece_witch_trial.jpg", "piece_bubble_witch", 360, 270, seed=6)

print("done")
