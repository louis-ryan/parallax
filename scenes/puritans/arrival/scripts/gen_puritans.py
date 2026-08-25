#!/usr/bin/env python3
"""
Procedural placeholder art for scenes/puritans/arrival.
Hudson River School wilderness background + comical caricature Puritans on a
wooden ship arriving at shore.

Stylized/abstract PLACEHOLDER (gradients + noise + hand-drawn shapes), not
painterly Hudson River School detail -- meant to get a correctly structured
layer stack into the FCPXML pipeline, replaceable later with real painted art.

Outputs (1920x1080):
  background.png   - opaque: sky, distant hills, forest, coastline (painting)
  water.png         - opaque or alpha: coastal water surface midground
  ship.png          - alpha: wooden ship with Puritan figures on deck, mid-frame
                       resting pose (positioned for a resting-near-shore point;
                       FCPXML will animate it sailing in from off-frame)
"""
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

random.seed(11)
np.random.seed(11)

W, H = 1920, 1080
OUT = "/Users/louisryan/Desktop/parallax/scenes/puritans/arrival/source_images"

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

# ---------------------------------------------------------------------------
# Background: Hudson River School sky -> hills -> forest -> shoreline
# ---------------------------------------------------------------------------
HORIZON_Y = int(H * 0.52)
SHORE_Y = int(H * 0.78)

def build_sky_gradient():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    px = img.load()
    stops = [
        (0.00, (90, 130, 175)),    # cool blue upper sky
        (0.25, (140, 170, 190)),   # softening
        (0.40, (225, 200, 160)),   # warm golden haze
        (0.52, (255, 225, 170)),   # bright horizon glow
        (0.55, (110, 130, 95)),    # distant hills, hazy blue-green
        (0.68, (70, 100, 60)),     # forest mid
        (0.78, (45, 70, 40)),      # forest near shore
        (1.00, (60, 80, 75)),      # water (overwritten by water layer, but blend ok)
    ]
    for y in range(H):
        t = y / H
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= t <= y1:
                lt = 0 if y1 == y0 else (t - y0) / (y1 - y0)
                color = lerp_color(c0, c1, lt)
                break
        else:
            color = stops[-1][1]
        for x in range(0, W, 4):
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = color
    return img

def draw_sun_glow(img):
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    sx, sy = int(W * 0.62), int(HORIZON_Y * 0.75)
    gdraw.ellipse([sx - 260, sy - 200, sx + 260, sy + 200], fill=(255, 235, 190, 160))
    gdraw.ellipse([sx - 110, sy - 90, sx + 110, sy + 90], fill=(255, 250, 220, 200))
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    img = Image.alpha_composite(img.convert("RGBA"), glow)
    return img.convert("RGB")

def draw_clouds(img):
    img = img.convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer, "RGBA")
    for _ in range(8):
        cx = random.randint(0, W)
        cy = random.randint(30, int(HORIZON_Y * 0.55))
        for _ in range(6):
            rx = random.randint(50, 110)
            ry = random.randint(14, 28)
            ox = cx + random.randint(-90, 90)
            oy = cy + random.randint(-14, 14)
            draw.ellipse([ox - rx, oy - ry, ox + rx, oy + ry], fill=(255, 245, 225, 90))
    layer = layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, layer)
    return img.convert("RGB")

def draw_distant_hills(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for layer_i, (y_base, color, amp) in enumerate([
        (int(H * 0.50), (120, 145, 130, 160), 30),
        (int(H * 0.54), (85, 115, 90, 200), 40),
    ]):
        pts = [(0, H)]
        x = 0
        while x <= W:
            pts.append((x, y_base + int(amp * math.sin(x * 0.003 + layer_i)) + random.randint(-8, 8)))
            x += 40
        pts.append((W, H))
        draw.polygon(pts, fill=color)
    return img

def draw_forest_treeline(img):
    draw = ImageDraw.Draw(img, "RGBA")
    base_y = int(H * 0.62)
    # rolling treeline silhouette
    pts = [(0, H)]
    x = 0
    while x <= W:
        pts.append((x, base_y + random.randint(-20, 25)))
        x += 25
    pts.append((W, H))
    draw.polygon(pts, fill=(35, 60, 32, 255))

    # individual tree clusters for texture near the treeline
    for _ in range(120):
        tx = random.randint(0, W)
        ty = base_y + random.randint(-15, 60)
        th = random.randint(20, 55)
        tw = int(th * 0.4)
        shade = random.randint(-10, 10)
        col = (30 + shade, 55 + shade, 28 + shade, 255)
        draw.polygon([(tx - tw, ty + th), (tx, ty), (tx + tw, ty + th)], fill=col)
    return img

def draw_shoreline(img):
    draw = ImageDraw.Draw(img, "RGBA")
    pts = [(0, H)]
    x = 0
    while x <= W:
        pts.append((x, SHORE_Y + random.randint(-10, 14)))
        x += 30
    pts.append((W, H))
    draw.polygon(pts, fill=(70, 60, 45, 255))
    # a few rocks along shore
    for _ in range(10):
        rx = random.randint(0, W)
        ry = SHORE_Y + random.randint(-4, 20)
        rw = random.randint(10, 26)
        draw.ellipse([rx - rw, ry - rw * 0.5, rx + rw, ry + rw * 0.5], fill=(55, 50, 45, 255))
    return img

def add_noise_texture(img, strength=6):
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-strength, strength + 1, arr.shape[:2])
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

# ---------------------------------------------------------------------------
# Water layer (separate, sits above background, below ship)
# ---------------------------------------------------------------------------
def build_water_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    top = SHORE_Y - 6
    stops = [
        (0.0, (150, 175, 165)),
        (0.4, (95, 130, 120)),
        (1.0, (55, 85, 80)),
    ]
    for y in range(top, H):
        t = (y - top) / max(1, (H - top))
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= t <= y1:
                lt = 0 if y1 == y0 else (t - y0) / (y1 - y0)
                color = lerp_color(c0, c1, lt)
                break
        else:
            color = stops[-1][1]
        draw.line([(0, y), (W, y)], fill=color + (255,))

    # gentle wave highlight streaks
    for _ in range(60):
        wx = random.randint(0, W)
        wy = random.randint(top + 10, H - 10)
        ww = random.randint(30, 90)
        draw.line([(wx - ww, wy), (wx + ww, wy + random.randint(-3, 3))],
                  fill=(210, 220, 210, 60), width=2)
    img = img.filter(ImageFilter.GaussianBlur(1.2))
    return img

# ---------------------------------------------------------------------------
# Ship + Puritans (alpha layer, subject)
# ---------------------------------------------------------------------------
def draw_ship_hull(draw, cx, base_y, scale=1.0):
    s = scale
    hull_color = (70, 48, 30, 255)
    hull_dark = (48, 32, 20, 255)
    # hull as a boat-shaped polygon
    pts = [
        (cx - 180 * s, base_y),
        (cx - 165 * s, base_y + 26 * s),
        (cx + 165 * s, base_y + 26 * s),
        (cx + 180 * s, base_y),
        (cx + 150 * s, base_y - 18 * s),
        (cx - 150 * s, base_y - 18 * s),
    ]
    draw.polygon(pts, fill=hull_color, outline=hull_dark)
    # waterline shading
    draw.polygon([
        (cx - 165 * s, base_y + 26 * s),
        (cx - 175 * s, base_y + 10 * s),
        (cx + 175 * s, base_y + 10 * s),
        (cx + 165 * s, base_y + 26 * s),
    ], fill=hull_dark)
    # deck line
    draw.line([(cx - 150 * s, base_y - 18 * s), (cx + 150 * s, base_y - 18 * s)],
              fill=(90, 65, 40, 255), width=int(3 * s))
    return base_y - 18 * s  # deck_y

def draw_ship_masts(draw, cx, deck_y, scale=1.0):
    s = scale
    mast_color = (60, 42, 26, 255)
    sail_color = (225, 215, 195, 235)
    sail_shadow = (190, 178, 158, 235)

    mast_positions = [cx - 70 * s, cx + 10 * s, cx + 90 * s]
    heights = [140 * s, 175 * s, 120 * s]
    sail_widths = [55 * s, 68 * s, 46 * s]

    for mx, mh, sw in zip(mast_positions, heights, sail_widths):
        draw.line([(mx, deck_y), (mx, deck_y - mh)], fill=mast_color, width=int(4 * s))
        # yard arm
        yard_y = deck_y - mh * 0.55
        draw.line([(mx - sw, yard_y), (mx + sw, yard_y)], fill=mast_color, width=int(2.5 * s))
        # sail as a billowing quad
        draw.polygon([
            (mx - sw * 0.9, yard_y),
            (mx + sw * 0.9, yard_y),
            (mx + sw * 0.65, yard_y + mh * 0.42),
            (mx - sw * 0.65, yard_y + mh * 0.42),
        ], fill=sail_color, outline=sail_shadow)
    return mast_positions[1], deck_y - heights[1]  # flag mount point


def draw_flag(draw, x, y, scale=1.0):
    s = scale
    draw.polygon([
        (x, y),
        (x + 22 * s, y + 4 * s),
        (x, y + 12 * s),
    ], fill=(140, 30, 30, 255))


def draw_puritan(draw, x, y, scale=1.0):
    """Comical rigid caricature: tall buckled hat, stiff posture, big white collar."""
    s = scale
    coat = (18, 18, 20, 255)
    skin = (235, 200, 170, 255)
    collar = (250, 250, 245, 255)
    hat_band = (90, 60, 30, 255)

    # legs (stiff, straight)
    draw.line([(x - 3 * s, y + 18 * s), (x - 3 * s, y + 34 * s)], fill=coat, width=int(3 * s))
    draw.line([(x + 3 * s, y + 18 * s), (x + 3 * s, y + 34 * s)], fill=coat, width=int(3 * s))
    # shoes
    draw.ellipse([x - 6 * s, y + 33 * s, x - 1 * s, y + 37 * s], fill=(20, 15, 10, 255))
    draw.ellipse([x + 1 * s, y + 33 * s, x + 6 * s, y + 37 * s], fill=(20, 15, 10, 255))

    # body (rigid rectangle-ish coat)
    draw.polygon([
        (x - 9 * s, y + 20 * s),
        (x - 8 * s, y - 6 * s),
        (x + 8 * s, y - 6 * s),
        (x + 9 * s, y + 20 * s),
    ], fill=coat)

    # arms straight down at sides
    draw.line([(x - 9 * s, y - 4 * s), (x - 10 * s, y + 16 * s)], fill=coat, width=int(3 * s))
    draw.line([(x + 9 * s, y - 4 * s), (x + 10 * s, y + 16 * s)], fill=coat, width=int(3 * s))
    draw.ellipse([x - 12 * s, y + 14 * s, x - 8 * s, y + 18 * s], fill=skin)
    draw.ellipse([x + 8 * s, y + 14 * s, x + 12 * s, y + 18 * s], fill=skin)

    # big white collar
    draw.polygon([
        (x - 11 * s, y - 5 * s),
        (x, y + 1 * s),
        (x + 11 * s, y - 5 * s),
        (x + 7 * s, y - 9 * s),
        (x, y - 4 * s),
        (x - 7 * s, y - 9 * s),
    ], fill=collar)

    # neck + head
    hx, hy = x, y - 14 * s
    draw.ellipse([hx - 5 * s, hy - 6 * s, hx + 5 * s, hy + 6 * s], fill=skin)

    # stern eyebrows + frown (comical stern face)
    draw.line([(hx - 3 * s, hy - 1 * s), (hx - 1 * s, hy - 2 * s)], fill=(20, 20, 20, 255), width=1)
    draw.line([(hx + 1 * s, hy - 2 * s), (hx + 3 * s, hy - 1 * s)], fill=(20, 20, 20, 255), width=1)
    draw.arc([hx - 3 * s, hy + 1 * s, hx + 3 * s, hy + 5 * s], start=200, end=340, fill=(20, 20, 20, 255))

    # tall buckled hat (the comical signature piece)
    brim_y = hy - 6 * s
    draw.ellipse([hx - 11 * s, brim_y - 2 * s, hx + 11 * s, brim_y + 2 * s], fill=coat)
    draw.polygon([
        (hx - 6 * s, brim_y),
        (hx - 6 * s, brim_y - 20 * s),
        (hx + 6 * s, brim_y - 20 * s),
        (hx + 6 * s, brim_y),
    ], fill=coat)
    draw.rectangle([hx - 3 * s, brim_y - 4 * s, hx + 3 * s, brim_y - 1 * s], fill=hat_band)
    # buckle
    draw.rectangle([hx - 2 * s, brim_y - 4 * s, hx + 2 * s, brim_y - 1 * s], outline=(200, 180, 60, 255), width=1)


def build_ship_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    cx = W // 2
    base_y = int(H * 0.80)
    scale = 1.9

    deck_y = draw_ship_hull(draw, cx, base_y, scale)
    flag_x, flag_y = draw_ship_masts(draw, cx, deck_y, scale)
    draw_flag(draw, flag_x, flag_y, scale)

    # small group of puritans on deck, roughly equal prominence
    puritan_positions = [
        (cx - 95, deck_y - 4, 1.5),
        (cx - 40, deck_y - 2, 1.6),
        (cx + 20, deck_y - 3, 1.55),
        (cx + 75, deck_y - 1, 1.5),
    ]
    for px, py, ps in puritan_positions:
        draw_puritan(draw, px, py, ps)

    img = img.filter(ImageFilter.GaussianBlur(0.4))
    return img

# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------
def main():
    bg = build_sky_gradient()
    bg = draw_sun_glow(bg)
    bg = draw_clouds(bg)
    bg = draw_distant_hills(bg)
    bg = draw_forest_treeline(bg)
    bg = draw_shoreline(bg)
    bg = add_noise_texture(bg, strength=6)
    bg = bg.filter(ImageFilter.GaussianBlur(0.5))
    bg = ImageEnhance.Color(bg).enhance(1.2)
    bg = ImageEnhance.Contrast(bg).enhance(1.08)
    bg.save(f"{OUT}/background.png")
    print("saved background.png", bg.size)

    water = build_water_layer()
    water.save(f"{OUT}/water.png")
    print("saved water.png", water.size)

    ship = build_ship_layer()
    ship.save(f"{OUT}/ship.png")
    print("saved ship.png", ship.size)

if __name__ == "__main__":
    main()
