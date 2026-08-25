import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

CANVAS = (1920, 1080)
GLOW_COLOR = (235, 195, 110, 255)
INK_COLOR = (250, 225, 170, 255)

def get_font(size):
    candidates = [
        "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
        "/System/Library/Fonts/Supplemental/Noteworthy.ttc",
        "/System/Library/Fonts/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    return ImageFont.load_default()

def jittered_text(draw, xy, text, font, seed, fill, char_spacing=None):
    rnd = random.Random(seed)
    x, y = xy
    for ch in text:
        dx = rnd.uniform(-1.2, 1.2)
        dy = rnd.uniform(-2.0, 2.0)
        draw.text((x + dx, y + dy), ch, font=font, fill=fill)
        w = draw.textlength(ch, font=font)
        x += w + (char_spacing or 0)

def make_text_piece(out_name, lines, seed, font_size=54, title=None):
    work_w, work_h = 700, 260
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))

    text_layer = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(text_layer)
    font = get_font(font_size)
    title_font = get_font(int(font_size * 0.75))

    cx = work_w / 2
    total_lines = len(lines) + (1 if title else 0)
    y = (work_h - total_lines * font_size * 1.3) / 2

    if title:
        tw = draw.textlength(title, font=title_font)
        jittered_text(draw, (cx - tw / 2, y), title, title_font, seed * 3, fill=(220, 150, 90, 255))
        y += font_size * 1.5
    for i, line in enumerate(lines):
        lw = draw.textlength(line, font=font)
        jittered_text(draw, (cx - lw / 2, y), line, font, seed * 7 + i, fill=INK_COLOR)
        y += font_size * 1.3

    # soft glow pass behind the crisp text
    glow = text_layer.filter(ImageFilter.GaussianBlur(6))
    glow_boost = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    glow_boost.paste(Image.new("RGBA", (work_w, work_h), GLOW_COLOR), (0, 0), glow.split()[3].point(lambda p: min(255, int(p * 1.4))))

    combined = Image.alpha_composite(glow_boost, text_layer)

    ox = (CANVAS[0] - work_w) // 2
    oy = (CANVAS[1] - work_h) // 2
    canvas.paste(combined, (ox, oy), combined)
    canvas.save(f"{out_name}.png")


make_text_piece("text_daniel_2300", ["Daniel 8:14", "2300 evenings", "and mornings"], seed=1, font_size=44)
make_text_piece("text_years", ["2300 − 457 = 1843", "± 1 yr = 1844"], seed=2, font_size=42)
make_text_piece("text_ezra", ["457 B.C.", "decree of Artaxerxes", "Ezra 7"], seed=3, font_size=42)
make_text_piece("text_numerology", ["7 × 70 wks", "= 490 yrs", "Daniel 9:24"], seed=4, font_size=42)

print("done")
