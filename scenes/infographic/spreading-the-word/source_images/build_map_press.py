#!/usr/bin/env python3
"""
Hero pieces for scenes/infographic/spreading-the-word: a paper-cutout US map
(background hero, fills most of the frame) and a steam printing press
silhouette sitting at its center. Same torn-paper-card + drop-shadow technique
as 1844-prophecy/build_equations.py's make_equation_piece, scaled up for a
hero-sized element.
"""
import random, math
from PIL import Image, ImageDraw, ImageFilter

random.seed(5)
CANVAS = (1920, 1080)
OUT = "/Users/louisryan/Desktop/parallax/scenes/infographic/spreading-the-word/source_images"

def torn_polygon(cx, cy, w, h, n=28, jitter=0.05, seed=0):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        angle = (2 * math.pi * i) / n
        rx = (w / 2) * (1 + rnd.uniform(-jitter, jitter))
        ry = (h / 2) * (1 + rnd.uniform(-jitter, jitter))
        pts.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    return pts

def paper_card(shape_draw_fn, w, h, seed, fill=(247, 240, 220, 255), shadow_offset=(8, 10)):
    """Generic torn-paper card: draws shape_draw_fn(draw, cx, cy) onto a card
    of size (w,h), adds the same blurred-offset drop shadow as the project's
    established technique, returns a full-CANVAS RGBA composite."""
    pad = 60
    work_w, work_h = w + pad * 2, h + pad * 2
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))

    card = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    cx, cy = work_w / 2, work_h / 2
    poly_pts = torn_polygon(cx, cy, w, h, seed=seed)
    draw.polygon(poly_pts, fill=fill)
    draw.polygon(poly_pts, outline=(150, 130, 95, 200))

    shape_draw_fn(draw, cx, cy)

    ox = (CANVAS[0] - work_w) // 2
    oy = (CANVAS[1] - work_h) // 2

    shadow_mask = Image.new("L", (work_w, work_h), 0)
    ImageDraw.Draw(shadow_mask).polygon(poly_pts, fill=255)
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(14))
    shadow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    shadow_fill = Image.new("RGBA", (work_w, work_h), (20, 15, 10, 140))
    shadow_layer = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    shadow_layer.paste(shadow_fill, (0, 0), shadow_mask)
    shadow.paste(shadow_layer, (ox + shadow_offset[0], oy + shadow_offset[1]), shadow_layer)
    canvas = Image.alpha_composite(canvas, shadow)

    card_shifted = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    card_shifted.paste(card, (ox, oy), card)
    canvas = Image.alpha_composite(canvas, card_shifted)
    return canvas


# ---------------------------------------------------------------------------
# US map silhouette (simplified/stylized, not geographically precise --
# paper-cutout style favors bold blobby shapes over fine detail per style.md)
# ---------------------------------------------------------------------------
def draw_us_map(draw, cx, cy):
    map_color = (200, 178, 140, 255)
    map_edge = (140, 118, 85, 255)
    # Simplified, deliberately stylized continental-US silhouette -- NOT
    # cartographically accurate (paper-cutout style favors bold blobby shapes,
    # per style.md). Built as a few simple, individually-safe (non-self-
    # intersecting) shapes composited together, rather than one large
    # hand-plotted perimeter polygon (which kept crossing itself) -- a wide
    # rounded body, plus a Texas notch, a Florida peninsula, and a Maine bump
    # as the recognizable landmarks that read "this is the US" at a glance.
    w, h = 1500, 700
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2

    # main body: rounded rectangle via a 12-point polygon, strictly clockwise
    r = 60
    body = [
        (x0 + r, y0), (x1 - r, y0), (x1, y0 + r),
        (x1, y1 - r), (x1 - r, y1), (x0 + r, y1),
        (x0, y1 - r), (x0, y0 + r),
    ]
    draw.polygon(body, fill=map_color, outline=map_edge)

    # Maine / New England bump -- a clear triangular spike jutting up and
    # right, straddling the top-right corner of the body so roughly half of
    # it sits outside the rectangle (unmistakably "a bump," not a corner
    # decoration sitting flush inside the edge).
    draw.polygon([
        (x1 - 90, y0 + 20),
        (x1 + 70, y0 - 90),
        (x1 + 10, y0 + 60),
    ], fill=map_color, outline=map_edge)

    # Florida peninsula -- long narrow triangle hanging well below the
    # bottom edge, positioned at roughly 75% across (clearly right-of-center).
    flx = x0 + w * 0.78
    draw.polygon([
        (flx - 60, y1 - 15),
        (flx + 40, y1 - 15),
        (flx - 10, y1 + 160),
    ], fill=map_color, outline=map_edge)

    # Texas notch -- a wide bulge pushing south of the bottom edge, centered
    # around 35% across (clearly left of Florida, well separated).
    txx = x0 + w * 0.35
    draw.polygon([
        (txx - 100, y1 - 15),
        (txx + 90, y1 - 15),
        (txx + 30, y1 + 130),
        (txx - 60, y1 + 80),
    ], fill=map_color, outline=map_edge)

    # rough state-line grid (interior only, jittered straight-ish segments,
    # suggests "map with borders" without needing accurate state shapes)
    rnd = random.Random(9)
    for _ in range(14):
        x0 = cx + rnd.uniform(-w * 0.4, w * 0.4)
        y0 = cy + rnd.uniform(-h * 0.32, h * 0.3)
        length = rnd.uniform(40, 140)
        angle = rnd.choice([0, math.pi / 2]) + rnd.uniform(-0.05, 0.05)
        x1 = x0 + length * math.cos(angle)
        y1 = y0 + length * math.sin(angle)
        draw.line([(x0, y0), (x1, y1)], fill=(160, 138, 100, 160), width=2)


def draw_printing_press(draw, cx, cy):
    """Steam printing press: cast-iron frame, flywheel, roller, small stack
    of newspapers at its base -- bold blobby silhouette per style.md."""
    iron = (35, 30, 28, 255)
    iron_hi = (60, 52, 46, 255)
    brass = (150, 110, 55, 255)
    paper = (240, 232, 210, 255)

    # base
    draw.rectangle([cx - 90, cy + 60, cx + 90, cy + 90], fill=iron)
    # main frame body (arched, classic Columbian-press silhouette)
    draw.polygon([
        (cx - 55, cy + 60), (cx - 55, cy - 20), (cx - 35, cy - 60),
        (cx + 35, cy - 60), (cx + 55, cy - 20), (cx + 55, cy + 60),
    ], fill=iron, outline=iron_hi)
    # flywheel
    draw.ellipse([cx - 28, cy - 100, cx + 28, cy - 44], outline=iron, width=10)
    draw.ellipse([cx - 6, cy - 78, cx + 6, cy - 66], fill=brass)
    # spokes
    for ang in range(0, 360, 60):
        a = math.radians(ang)
        x1, y1 = cx + 6 * math.cos(a), cy - 72 + 6 * math.sin(a)
        x2, y2 = cx + 26 * math.cos(a), cy - 72 + 26 * math.sin(a)
        draw.line([(x1, y1), (x2, y2)], fill=iron, width=4)
    # top platen bar
    draw.rectangle([cx - 60, cy - 66, cx + 60, cy - 58], fill=iron_hi)
    # lever arm
    draw.line([(cx + 55, cy - 30), (cx + 110, cy - 55)], fill=iron, width=8)
    draw.ellipse([cx + 104, cy - 62, cx + 118, cy - 48], fill=brass)

    # small stack of printed newspapers at the base
    for i in range(4):
        yy = cy + 55 - i * 6
        draw.rectangle([cx - 40 + i * 3, yy, cx + 10 + i * 3, yy + 6], fill=paper, outline=(180, 165, 130, 255))


def draw_newspaper(cx, cy, scale=1.0, angle=0):
    """A single flying newspaper sheet with a bold doomsday headline block."""
    s = scale
    paper = (238, 228, 200, 255)
    paper_shadow = (205, 192, 160, 255)
    ink = (40, 32, 22, 255)
    ink_red = (110, 30, 25, 255)

    img = Image.new("RGBA", (int(260 * s), int(180 * s)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = img.size
    # slightly curled/folded sheet silhouette (two overlapping offset rects)
    d.polygon([(6, 10), (w - 4, 0), (w - 8, h - 8), (2, h - 2)], fill=paper_shadow)
    d.polygon([(0, 4), (w - 10, 0), (w - 4, h - 12), (6, h - 4)], fill=paper)
    # masthead bar
    d.rectangle([12, 10, w - 12, 32], outline=ink, width=2)
    d.line([(10, 40), (w - 14, 38)], fill=ink, width=2)
    # bold doomsday headline block (thick jittered strokes standing in for
    # large headline type -- paper-cutout style avoids fine real text at this
    # scale, per style.md's "bold simple silhouettes" rule)
    rnd = random.Random(int(cx + cy))
    for i in range(3):
        yy = 50 + i * 22
        xx = 16 + rnd.uniform(-2, 2)
        ww = rnd.uniform(0.55, 0.85) * (w - 32)
        d.rectangle([xx, yy, xx + ww, yy + 12], fill=ink_red if i == 0 else ink)
    img = img.rotate(angle, expand=True, resample=Image.BICUBIC)
    return img


def make_flame_burst(out_name, cx, cy, height_scale=1.0, glow_scale=1.0):
    """Doomsday 'catching fire' landing burst -- identical technique to
    1844-prophecy/build_flame.py's make_flame_frame, reused here at each
    newspaper's arrival point on the map."""
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    glow = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    glow_r = int(55 * glow_scale)
    gd.ellipse([cx - glow_r, cy - glow_r, cx + glow_r, cy + glow_r], fill=(255, 170, 60, 130))
    glow = glow.filter(ImageFilter.GaussianBlur(24))
    canvas = Image.alpha_composite(canvas, glow)

    flame = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    fd = ImageDraw.Draw(flame)
    fh = int(34 * height_scale)
    fw = int(12 * height_scale)
    fd.ellipse([cx - fw, cy - fh, cx + fw, cy + int(fh * 0.3)], fill=(255, 140, 30, 230))
    fw2, fh2 = int(fw * 0.5), int(fh * 0.55)
    fd.ellipse([cx - fw2, cy - fh2, cx + fw2, cy + int(fh2 * 0.3)], fill=(255, 235, 160, 240))
    flame = flame.filter(ImageFilter.GaussianBlur(1.3))
    canvas = Image.alpha_composite(canvas, flame)
    canvas.save(f"{OUT}/{out_name}.png")


# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    W, H = CANVAS
    cx, cy = W // 2, H // 2

    # us_map.png is generated by build_real_map.py (real US state-boundary
    # geometry), not here -- run that script first/separately. This script's
    # earlier hand-plotted draw_us_map()/torn_polygon() approximation is kept
    # only as the shared paper_card() torn-edge helper's original source, no
    # longer invoked.

    press = paper_card(draw_printing_press, 340, 300, seed=2,
                        fill=(235, 225, 200, 255), shadow_offset=(6, 8))
    press.save(f"{OUT}/press.png")
    print("saved press.png")

    # newspaper pieces flying to distributed arrival points across the map.
    # Rest positions are true-pixel offsets from frame center, computed to
    # land on real, period-plausible 19th-century American cities (verified
    # against the actual US landmass geometry in build_real_map.py -- the
    # earlier hand-picked compass-point offsets fell outside the real,
    # narrower US outline once that replaced the rectangular approximation).
    NEWSPAPER_TARGETS = [
        ("newspaper_ne",  644, -133, -18),   # Boston
        ("newspaper_se",  383,  134,  14),   # Savannah
        ("newspaper_nw", -697, -215,  22),   # Portland, OR
        ("newspaper_sw",  -69,  204, -16),   # San Antonio
        ("newspaper_mw",  213, -120,   8),   # Chicago
        ("newspaper_c",   147,  -36, -10),   # St. Louis
        ("newspaper_s",   150,  190,  20),   # New Orleans
    ]
    for name, dx, dy, angle in NEWSPAPER_TARGETS:
        np_img = draw_newspaper(cx + dx, cy + dy, scale=1.0, angle=angle)
        canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
        px = cx + dx - np_img.width // 2
        py = cy + dy - np_img.height // 2
        canvas.paste(np_img, (px, py), np_img)
        canvas.save(f"{OUT}/{name}.png")
        print(f"saved {name}.png")

    # flame-glow bursts at each newspaper's landing point (three stepped
    # variants per burst site for the flicker, matching 1844-prophecy)
    for name, dx, dy, _ in NEWSPAPER_TARGETS:
        bx, by = cx + dx, cy + dy
        make_flame_burst(f"burst_{name}_a", bx, by, height_scale=1.0, glow_scale=1.0)
        make_flame_burst(f"burst_{name}_b", bx, by, height_scale=1.2, glow_scale=1.15)
        make_flame_burst(f"burst_{name}_c", bx, by, height_scale=0.8, glow_scale=0.85)
    print("saved all flame bursts")

    print("done")
