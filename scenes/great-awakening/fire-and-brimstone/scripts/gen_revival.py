#!/usr/bin/env python3
"""
Procedural placeholder art for scenes/great-awakening/fire-and-brimstone.
19th-century outdoor tent revival at dusk: preacher elevated on a pulpit, arm
raised mid-shout, dense uniform crowd below with raised arms and upturned faces,
torchlight rim-lighting cutting through the dark.

Stylized/abstract PLACEHOLDER (gradients + noise + hand-drawn shapes), not
painterly detail -- meant to get a correctly structured layer stack into the
FCPXML pipeline, replaceable later with real painted art.

Lesson applied from inferno/satan-bound: dark figures on a dark background are
illegible without deliberate torch/backlight rim-lighting -- glow layers are
built and composited FIRST behind every figure group, then rim-lit outlines,
then body fills, same as the fixed inferno approach.

Outputs (1920x1080):
  background.png   - opaque: dusk sky, treeline, tent structure
  torchlight.png    - alpha: flickering torch/lantern glow (additive)
  crowd_left.png    - alpha: congregation figures, left half, slides in from left
  crowd_right.png   - alpha: congregation figures, right half, slides in from right
  preacher.png      - alpha: preacher on pulpit, focal point
"""
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

random.seed(77)
np.random.seed(77)

W, H = 1920, 1080
OUT = "/Users/louisryan/Desktop/parallax/scenes/great-awakening/fire-and-brimstone/source_images"

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

HORIZON_Y = int(H * 0.55)
GROUND_Y = int(H * 0.62)
PULPIT_X = W // 2

# ---------------------------------------------------------------------------
# Background: dusk sky, treeline, tent framework
# ---------------------------------------------------------------------------
def build_sky_gradient():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    px = img.load()
    stops = [
        (0.00, (25, 20, 45)),      # deep blue-violet dusk
        (0.30, (55, 35, 60)),      # transitioning
        (0.48, (140, 70, 60)),     # warm dusk band
        (0.55, (90, 50, 40)),      # near horizon, dimming warmth
        (0.62, (35, 24, 22)),      # treeline dark
        (1.00, (18, 14, 14)),      # ground, near black
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

def draw_stars(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(60):
        x = random.randint(0, W)
        y = random.randint(0, int(HORIZON_Y * 0.6))
        b = random.randint(120, 220)
        draw.point((x, y), fill=(b, b, min(255, b + 20), 255))
    return img

def draw_treeline(img):
    draw = ImageDraw.Draw(img, "RGBA")
    pts = [(0, H)]
    x = 0
    base_y = GROUND_Y - 10
    while x <= W:
        pts.append((x, base_y + random.randint(-30, 15)))
        x += 30
    pts.append((W, H))
    draw.polygon(pts, fill=(15, 11, 12, 255))
    return img

def draw_tent_structure(img):
    """A simple large canvas revival tent silhouette behind/around the pulpit."""
    draw = ImageDraw.Draw(img, "RGBA")
    apex_x, apex_y = PULPIT_X, int(H * 0.32)
    base_y = GROUND_Y + 20
    tent_color = (30, 22, 20, 235)
    tent_shadow = (18, 13, 12, 235)

    # main tent triangle (canopy)
    draw.polygon([
        (apex_x, apex_y),
        (apex_x - 520, base_y),
        (apex_x + 520, base_y),
    ], fill=tent_color)
    # ridge shading
    draw.polygon([
        (apex_x, apex_y),
        (apex_x - 60, base_y),
        (apex_x + 60, base_y),
    ], fill=tent_shadow)
    # support poles
    for px in [apex_x - 480, apex_x - 240, apex_x + 240, apex_x + 480]:
        draw.line([(px, base_y), (px, base_y - 40)], fill=(20, 14, 12, 255), width=6)
    return img

def draw_covered_wagon(draw, x, base_y, scale=1.0, facing=1):
    s = scale
    wood = (50, 34, 22, 255)
    wood_dark = (32, 20, 12, 255)
    canvas = (170, 155, 125, 240)
    canvas_shadow = (135, 120, 95, 240)
    wheel = (25, 16, 10, 255)

    # wheels
    for wx in (x - 16 * s, x + 14 * s):
        draw.ellipse([wx - 7 * s, base_y - 14 * s, wx + 7 * s, base_y], outline=wheel, width=max(1, int(2 * s)))
        draw.ellipse([wx - 2 * s, base_y - 9 * s, wx + 2 * s, base_y - 5 * s], fill=wheel)

    # bed
    draw.rectangle([x - 20 * s, base_y - 20 * s, x + 18 * s, base_y - 12 * s], fill=wood, outline=wood_dark)

    # canvas canopy (bowed top, classic covered-wagon silhouette)
    canopy_top = base_y - 40 * s
    draw.polygon([
        (x - 18 * s, base_y - 12 * s),
        (x - 15 * s, canopy_top),
        (x + 13 * s, canopy_top),
        (x + 16 * s, base_y - 12 * s),
    ], fill=canvas, outline=canvas_shadow)
    # canopy ribs
    for i in range(3):
        rx = x - 12 * s + i * 12 * s
        draw.line([(rx, base_y - 12 * s), (rx, canopy_top + 3 * s)], fill=canvas_shadow, width=1)

    # yoke/tongue pointing the facing direction
    draw.line([(x - 20 * s * facing, base_y - 16 * s), (x - 34 * s * facing, base_y - 6 * s)],
              fill=wood_dark, width=max(1, int(2 * s)))


def draw_horse(draw, x, base_y, scale=1.0, facing=1):
    s = scale
    body = (35, 24, 16, 255)
    # legs
    for lx in (-5, -1, 3, 7):
        draw.line([(x + lx * s, base_y - 10 * s), (x + lx * s, base_y)], fill=body, width=max(1, int(1.5 * s)))
    # body
    draw.ellipse([x - 10 * s, base_y - 18 * s, x + 9 * s, base_y - 8 * s], fill=body)
    # neck + head
    nx = x + 9 * s * facing
    draw.line([(nx - 2 * s * facing, base_y - 16 * s), (nx + 5 * s * facing, base_y - 24 * s)],
              fill=body, width=max(2, int(3 * s)))
    head_x0 = min(nx + 2 * s * facing, nx + 8 * s * facing)
    head_x1 = max(nx + 2 * s * facing, nx + 8 * s * facing)
    draw.ellipse([head_x0, base_y - 27 * s, head_x1, base_y - 21 * s], fill=body)
    # tail
    draw.line([(x - 10 * s, base_y - 16 * s), (x - 14 * s, base_y - 6 * s)], fill=body, width=max(1, int(2 * s)))


def draw_wagon_camp(img):
    """Covered wagons and horses at the fringe of the clearing -- frontier
    signifier. Placed fully outside the crowd's x-range (see build_crowd_layer
    call in main()) and given their own warm glow so they stay legible against
    the dark ground rather than reading as a dim smudge."""
    img = img.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    wagon_y = GROUND_Y + 10
    for gx in (110, W - 110):
        gd.ellipse([gx - 130, wagon_y - 90, gx + 130, wagon_y + 30], fill=(255, 140, 60, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img, "RGBA")
    # left cluster, fully clear of the crowd (which starts at x=210)
    draw_covered_wagon(draw, 90, wagon_y, scale=1.7, facing=1)
    draw_horse(draw, 175, wagon_y + 6, scale=1.4, facing=-1)
    # right cluster, fully clear of the crowd (which ends at x=W-210)
    draw_covered_wagon(draw, W - 90, wagon_y, scale=1.7, facing=-1)
    draw_horse(draw, W - 175, wagon_y + 6, scale=1.4, facing=1)
    return img.convert("RGB")


def draw_split_rail_fence(img):
    """Rustic split-rail fence bordering the meeting ground clearing."""
    draw = ImageDraw.Draw(img, "RGBA")
    fence_color = (40, 28, 18, 220)
    fence_y = GROUND_Y + 26
    for seg_x in range(0, W, 34):
        # skip where wagons sit
        if 30 < seg_x < 300 or W - 300 < seg_x < W - 20:
            continue
        post_h = 16
        draw.line([(seg_x, fence_y), (seg_x, fence_y - post_h)], fill=fence_color, width=3)
        draw.line([(seg_x - 2, fence_y - post_h * 0.75), (seg_x + 30, fence_y - post_h * 0.65)],
                   fill=fence_color, width=2)
        draw.line([(seg_x - 2, fence_y - post_h * 0.35), (seg_x + 30, fence_y - post_h * 0.25)],
                   fill=fence_color, width=2)
    return img


def draw_distant_church(img):
    """Small white clapboard church + steeple silhouette on the horizon,
    lit slightly warmer/brighter than the treeline so it reads as a distinct
    landmark rather than disappearing into the dark hills."""
    draw = ImageDraw.Draw(img, "RGBA")
    cx = int(W * 0.16)
    base_y = int(H * 0.565)
    church_color = (95, 70, 55, 235)
    trim = (140, 110, 85, 235)
    # body
    draw.polygon([(cx - 20, base_y), (cx - 20, base_y - 22), (cx + 20, base_y - 22), (cx + 20, base_y)],
                 fill=church_color, outline=trim)
    # roof
    draw.polygon([(cx - 23, base_y - 22), (cx, base_y - 36), (cx + 23, base_y - 22)],
                 fill=church_color, outline=trim)
    # steeple
    draw.rectangle([cx - 4, base_y - 56, cx + 4, base_y - 22], fill=church_color, outline=trim)
    draw.polygon([(cx - 7, base_y - 56), (cx, base_y - 68), (cx + 7, base_y - 56)],
                 fill=church_color, outline=trim)
    return img


def add_noise_texture(img, strength=6):
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-strength, strength + 1, arr.shape[:2])
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

# ---------------------------------------------------------------------------
# Torchlight layer (alpha, additive, flicker source)
# ---------------------------------------------------------------------------
TORCH_POSITIONS = [
    (280, GROUND_Y + 40, 1.0), (620, GROUND_Y + 60, 0.85),
    (1300, GROUND_Y + 60, 0.85), (1640, GROUND_Y + 40, 1.0),
    (PULPIT_X - 140, GROUND_Y - 60, 0.9), (PULPIT_X + 140, GROUND_Y - 60, 0.9),
]

def build_torchlight_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    for tx, ty, scale in TORCH_POSITIONS:
        # broad soft glow pool
        glow_r = int(140 * scale)
        for _ in range(1):
            pass
        gdraw_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gdraw_layer)
        gd.ellipse([tx - glow_r, ty - glow_r * 1.4, tx + glow_r, ty + glow_r * 0.6],
                   fill=(255, 150, 50, 140))
        gdraw_layer = gdraw_layer.filter(ImageFilter.GaussianBlur(35))
        img = Image.alpha_composite(img, gdraw_layer)

        # flame core
        fh = int(50 * scale)
        fw = int(fh * 0.35)
        pts = [
            (tx - fw, ty),
            (tx - fw * 0.4, ty - fh * 0.6),
            (tx, ty - fh),
            (tx + fw * 0.4, ty - fh * 0.6),
            (tx + fw, ty),
        ]
        draw.polygon(pts, fill=(255, 170, 60, 240))

    # dramatic uplight glow behind/around the preacher on pulpit
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([PULPIT_X - 220, int(H * 0.30), PULPIT_X + 220, int(H * 0.62)],
               fill=(255, 160, 70, 110))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(glow, img)

    img = img.filter(ImageFilter.GaussianBlur(1.5))
    return img

# ---------------------------------------------------------------------------
# Crowd figures: dense, uniform, rim-lit silhouettes with raised arms
# ---------------------------------------------------------------------------
def draw_congregant_man(draw, x, y, scale=1.0, arms_up=True, kneeling=False):
    """Period silhouette: dark knee-length coat, trousers, wide-brim or top hat."""
    s = scale
    body = (14, 10, 9, 255)
    rim = (255, 150, 60, 190)
    rim_w = max(1, int(1.3 * s))
    skin_lit = (235, 190, 150, 220)

    def rim_line(p1, p2, width):
        draw.line([p1, p2], fill=rim, width=width + rim_w * 2)

    def body_line(p1, p2, width):
        draw.line([p1, p2], fill=body, width=width)

    leg_top_y = y if not kneeling else y - 6 * s
    # legs (trousers)
    l1 = ((x - 2 * s, leg_top_y), (x - 4 * s, y + 18 * s))
    l2 = ((x + 2 * s, leg_top_y), (x + 4 * s, y + 18 * s))
    rim_line(*l1, int(3 * s)); rim_line(*l2, int(3 * s))
    body_line(*l1, int(3 * s)); body_line(*l2, int(3 * s))

    # knee-length frock coat torso, slightly flared at hem
    coat = [
        (x - 5 * s, leg_top_y - 18 * s),
        (x - 4 * s, leg_top_y),
        (x - 8 * s, leg_top_y + 6 * s),
        (x + 8 * s, leg_top_y + 6 * s),
        (x + 4 * s, leg_top_y),
        (x + 5 * s, leg_top_y - 18 * s),
    ]
    cxp = sum(p[0] for p in coat) / len(coat)
    cyp = sum(p[1] for p in coat) / len(coat)
    rim_poly = []
    for px, py in coat:
        dx, dy = px - cxp, py - cyp
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        rim_poly.append((px + dx / dist * (rim_w + 1.5 * s), py + dy / dist * (rim_w + 1.5 * s)))
    draw.polygon(rim_poly, fill=rim)
    draw.polygon(coat, fill=body)

    # head
    hx, hy = x, leg_top_y - 23 * s
    head_box = [hx - 3.2 * s, hy - 3.2 * s, hx + 3.2 * s, hy + 3.2 * s]
    rim_box = [b - rim_w if i < 2 else b + rim_w for i, b in enumerate(head_box)]
    draw.ellipse(rim_box, fill=rim)
    draw.ellipse(head_box, fill=skin_lit)

    # hat: alternate wide-brim vs. top hat for variety
    if int((x + y) // 7) % 2 == 0:
        # wide-brim hat
        brim_y = hy - 3 * s
        draw.ellipse([hx - 6.5 * s, brim_y - 1.2 * s, hx + 6.5 * s, brim_y + 1.2 * s], fill=body)
        draw.polygon([(hx - 3 * s, brim_y), (hx - 3 * s, brim_y - 5 * s),
                      (hx + 3 * s, brim_y - 5 * s), (hx + 3 * s, brim_y)], fill=body)
    else:
        # top hat
        brim_y = hy - 3 * s
        draw.ellipse([hx - 4.5 * s, brim_y - 0.8 * s, hx + 4.5 * s, brim_y + 0.8 * s], fill=body)
        draw.rectangle([hx - 2.6 * s, brim_y - 8 * s, hx + 2.6 * s, brim_y], fill=body)

    if arms_up:
        a1 = ((x - 4 * s, leg_top_y - 14 * s), (x - 9 * s, leg_top_y - 28 * s))
        a2 = ((x + 4 * s, leg_top_y - 14 * s), (x + 9 * s, leg_top_y - 28 * s))
        rim_line(*a1, int(2.3 * s)); rim_line(*a2, int(2.3 * s))
        body_line(*a1, int(2.3 * s)); body_line(*a2, int(2.3 * s))
    else:
        a1 = ((x - 4 * s, leg_top_y - 14 * s), (x - 6 * s, leg_top_y - 3 * s))
        a2 = ((x + 4 * s, leg_top_y - 14 * s), (x + 6 * s, leg_top_y - 3 * s))
        rim_line(*a1, int(2.3 * s)); rim_line(*a2, int(2.3 * s))
        body_line(*a1, int(2.3 * s)); body_line(*a2, int(2.3 * s))


def draw_congregant_woman(draw, x, y, scale=1.0, arms_up=True, kneeling=False):
    """Period silhouette: bonnet, full high-necked long skirt, shawl."""
    s = scale
    body = (16, 11, 10, 255)
    rim = (255, 150, 60, 190)
    rim_w = max(1, int(1.3 * s))
    skin_lit = (235, 190, 150, 220)
    shawl = (60, 40, 30, 255)

    def rim_line(p1, p2, width):
        draw.line([p1, p2], fill=rim, width=width + rim_w * 2)

    def body_line(p1, p2, width):
        draw.line([p1, p2], fill=body, width=width)

    hem_y = (y if not kneeling else y - 6 * s) + 18 * s
    waist_y = hem_y - 18 * s

    # full bell-shaped skirt (the defining period silhouette)
    skirt = [
        (x - 3 * s, waist_y),
        (x - 11 * s, hem_y),
        (x + 11 * s, hem_y),
        (x + 3 * s, waist_y),
    ]
    cxp = sum(p[0] for p in skirt) / len(skirt)
    cyp = sum(p[1] for p in skirt) / len(skirt)
    rim_poly = []
    for px, py in skirt:
        dx, dy = px - cxp, py - cyp
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        rim_poly.append((px + dx / dist * (rim_w + 1.5 * s), py + dy / dist * (rim_w + 1.5 * s)))
    draw.polygon(rim_poly, fill=rim)
    draw.polygon(skirt, fill=body)

    # bodice
    bodice_box = [x - 4.5 * s, waist_y - 14 * s, x + 4.5 * s, waist_y + 2 * s]
    rim_box = [b - rim_w if i < 2 else b + rim_w for i, b in enumerate(bodice_box)]
    draw.ellipse(rim_box, fill=rim)
    draw.ellipse(bodice_box, fill=body)

    # shawl over shoulders
    draw.polygon([
        (x - 6 * s, waist_y - 12 * s), (x, waist_y - 6 * s), (x + 6 * s, waist_y - 12 * s),
        (x + 4 * s, waist_y - 2 * s), (x, waist_y - 5 * s), (x - 4 * s, waist_y - 2 * s),
    ], fill=shawl)

    # head
    hx, hy = x, waist_y - 17 * s
    head_box = [hx - 3 * s, hy - 3 * s, hx + 3 * s, hy + 3 * s]
    rim_box = [b - rim_w if i < 2 else b + rim_w for i, b in enumerate(head_box)]
    draw.ellipse(rim_box, fill=rim)
    draw.ellipse(head_box, fill=skin_lit)

    # bonnet (defining accessory)
    draw.pieslice([hx - 4.5 * s, hy - 5.5 * s, hx + 4.5 * s, hy + 3 * s], 180, 360, fill=body)
    draw.line([(hx - 4 * s, hy - 1 * s), (hx - 5.5 * s, hy + 4 * s)], fill=(200, 180, 150, 255), width=1)
    draw.line([(hx + 4 * s, hy - 1 * s), (hx + 5.5 * s, hy + 4 * s)], fill=(200, 180, 150, 255), width=1)

    if arms_up:
        a1 = ((x - 4 * s, waist_y - 10 * s), (x - 8 * s, waist_y - 22 * s))
        a2 = ((x + 4 * s, waist_y - 10 * s), (x + 8 * s, waist_y - 22 * s))
        rim_line(*a1, int(2 * s)); rim_line(*a2, int(2 * s))
        body_line(*a1, int(2 * s)); body_line(*a2, int(2 * s))
    else:
        a1 = ((x - 4 * s, waist_y - 10 * s), (x - 5 * s, waist_y - 1 * s))
        a2 = ((x + 4 * s, waist_y - 10 * s), (x + 5 * s, waist_y - 1 * s))
        rim_line(*a1, int(2 * s)); rim_line(*a2, int(2 * s))
        body_line(*a1, int(2 * s)); body_line(*a2, int(2 * s))


def build_crowd_layer(x_range, n_figures, seed_offset=0):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(1000 + seed_offset)
    rows = [
        (GROUND_Y + 30, 3.4, 0.85),
        (GROUND_Y + 55, 2.9, 0.78),
        (GROUND_Y + 78, 2.5, 0.7),
        (GROUND_Y + 98, 2.1, 0.6),
    ]
    count = 0
    for row_y, scale, arm_prob in rows:
        n_in_row = n_figures // len(rows)
        x0, x1 = x_range
        for i in range(n_in_row):
            x = x0 + (x1 - x0) * (i / max(1, n_in_row - 1)) + rng.randint(-14, 14)
            arms_up = rng.random() < arm_prob
            kneel = rng.random() < 0.08
            if rng.random() < 0.5:
                draw_congregant_man(draw, x, row_y, scale, arms_up=arms_up, kneeling=kneel)
            else:
                draw_congregant_woman(draw, x, row_y, scale, arms_up=arms_up, kneeling=kneel)
            count += 1
    return img

# ---------------------------------------------------------------------------
# Preacher: elevated on pulpit, arm raised, dramatically lit
# ---------------------------------------------------------------------------
def draw_pulpit(draw, cx, base_y, scale=1.0):
    s = scale
    wood = (45, 30, 20, 255)
    wood_dark = (28, 18, 12, 255)
    draw.polygon([
        (cx - 24 * s, base_y), (cx - 20 * s, base_y - 30 * s),
        (cx + 20 * s, base_y - 30 * s), (cx + 24 * s, base_y),
    ], fill=wood, outline=wood_dark)
    draw.rectangle([cx - 26 * s, base_y - 34 * s, cx + 26 * s, base_y - 28 * s], fill=wood_dark)
    return base_y - 34 * s  # standing surface y

def draw_preacher(draw, x, stand_y, scale=1.0):
    s = scale
    coat = (10, 8, 8, 255)
    rim = (255, 190, 100, 230)
    rim_w = max(2, int(2 * s))
    skin = (240, 205, 170, 255)

    def rim_line(p1, p2, width):
        draw.line([p1, p2], fill=rim, width=width + rim_w * 2)

    def body_line(p1, p2, width):
        draw.line([p1, p2], fill=coat, width=width)

    # legs planted
    l1 = ((x - 5 * s, stand_y), (x - 5 * s, stand_y - 22 * s))
    l2 = ((x + 5 * s, stand_y), (x + 5 * s, stand_y - 22 * s))
    rim_line(*l1, int(5 * s)); rim_line(*l2, int(5 * s))
    body_line(*l1, int(5 * s)); body_line(*l2, int(5 * s))

    # frock coat tails (split at the front, hanging past the waist -- the
    # defining 19th-century preacher silhouette)
    tail_l = [(x - 4 * s, stand_y - 34 * s), (x - 14 * s, stand_y - 20 * s), (x - 2 * s, stand_y - 30 * s)]
    tail_r = [(x + 4 * s, stand_y - 34 * s), (x + 14 * s, stand_y - 20 * s), (x + 2 * s, stand_y - 30 * s)]
    draw.polygon(tail_l, fill=coat)
    draw.polygon(tail_r, fill=coat)

    # long coat torso
    torso = [
        (x - 14 * s, stand_y - 22 * s),
        (x - 12 * s, stand_y - 60 * s),
        (x, stand_y - 68 * s),
        (x + 12 * s, stand_y - 60 * s),
        (x + 14 * s, stand_y - 22 * s),
    ]
    cxp = sum(p[0] for p in torso) / len(torso)
    cyp = sum(p[1] for p in torso) / len(torso)
    expanded = []
    for px, py in torso:
        dx, dy = px - cxp, py - cyp
        dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        expanded.append((px + dx / dist * (rim_w + 3), py + dy / dist * (rim_w + 3)))
    draw.polygon(expanded, fill=rim)
    draw.polygon(torso, fill=coat)

    # waistcoat panel + buttons, visible under the open coat front
    waistcoat = (35, 22, 15, 255)
    draw.polygon([
        (x - 5 * s, stand_y - 58 * s), (x - 4 * s, stand_y - 26 * s),
        (x + 4 * s, stand_y - 26 * s), (x + 5 * s, stand_y - 58 * s),
    ], fill=waistcoat)
    for by in range(3):
        byy = stand_y - 52 * s + by * 8 * s
        draw.ellipse([x - 1 * s, byy, x + 1 * s, byy + 2 * s], fill=(200, 180, 130, 255))

    # cravat / high collar knot at the throat
    draw.polygon([
        (x - 3 * s, stand_y - 60 * s), (x, stand_y - 55 * s), (x + 3 * s, stand_y - 60 * s),
    ], fill=(235, 228, 210, 255))

    # one arm raised high (fist), one arm down gripping a book
    raised = ((x - 10 * s, stand_y - 58 * s), (x - 26 * s, stand_y - 96 * s))
    rim_line(*raised, int(4 * s))
    body_line(*raised, int(4 * s))
    draw.ellipse([x - 30 * s, stand_y - 102 * s, x - 20 * s, stand_y - 92 * s], fill=skin)

    down_arm = ((x + 10 * s, stand_y - 58 * s), (x + 16 * s, stand_y - 40 * s))
    rim_line(*down_arm, int(4 * s))
    body_line(*down_arm, int(4 * s))
    draw.ellipse([x + 12 * s, stand_y - 42 * s, x + 20 * s, stand_y - 34 * s], fill=skin)
    draw.rectangle([x + 10 * s, stand_y - 40 * s, x + 20 * s, stand_y - 32 * s],
                   fill=(200, 190, 160, 255))  # book

    # head, mouth open mid-shout
    hx, hy = x, stand_y - 74 * s
    head_box = [hx - 8 * s, hy - 9 * s, hx + 8 * s, hy + 9 * s]
    rim_box = [b - rim_w if i < 2 else b + rim_w for i, b in enumerate(head_box)]
    draw.ellipse(rim_box, fill=rim)
    draw.ellipse(head_box, fill=skin)
    # wild hair
    for i in range(7):
        angle = math.pi * (0.15 + 0.7 * i / 6)
        hxp = hx + math.cos(angle) * 9 * s
        hyp = hy - abs(math.sin(angle)) * 10 * s - 2 * s
        draw.line([(hx, hy - 6 * s), (hxp, hyp)], fill=(30, 25, 22, 255), width=int(1.5 * s))
    # open mouth
    draw.ellipse([hx - 2.5 * s, hy + 1 * s, hx + 2.5 * s, hy + 6 * s], fill=(60, 20, 20, 255))
    # brows, intense
    draw.line([(hx - 5 * s, hy - 3 * s), (hx - 1 * s, hy - 5 * s)], fill=(20, 15, 12, 255), width=1)
    draw.line([(hx + 1 * s, hy - 5 * s), (hx + 5 * s, hy - 3 * s)], fill=(20, 15, 12, 255), width=1)


def build_preacher_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    base_y = GROUND_Y + 10
    stand_y = draw_pulpit(draw, PULPIT_X, base_y, scale=2.2)
    draw_preacher(draw, PULPIT_X, stand_y, scale=2.2)
    img = img.filter(ImageFilter.GaussianBlur(0.3))
    return img

# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------
def main():
    bg = build_sky_gradient()
    bg = draw_stars(bg)
    bg = draw_treeline(bg)
    bg = draw_distant_church(bg)
    bg = draw_tent_structure(bg)
    bg = draw_split_rail_fence(bg)
    bg = draw_wagon_camp(bg)
    bg = add_noise_texture(bg, strength=6)
    bg = bg.filter(ImageFilter.GaussianBlur(0.5))
    bg = ImageEnhance.Color(bg).enhance(1.15)
    bg = ImageEnhance.Contrast(bg).enhance(1.1)
    bg.save(f"{OUT}/background.png")
    print("saved background.png", bg.size)

    torch = build_torchlight_layer()
    torch.save(f"{OUT}/torchlight.png")
    print("saved torchlight.png", torch.size)

    crowd_left = build_crowd_layer((210, PULPIT_X - 160), 40, seed_offset=1)
    crowd_left.save(f"{OUT}/crowd_left.png")
    print("saved crowd_left.png", crowd_left.size)

    crowd_right = build_crowd_layer((PULPIT_X + 160, W - 210), 40, seed_offset=2)
    crowd_right.save(f"{OUT}/crowd_right.png")
    print("saved crowd_right.png", crowd_right.size)

    preacher = build_preacher_layer()
    preacher.save(f"{OUT}/preacher.png")
    print("saved preacher.png", preacher.size)

if __name__ == "__main__":
    main()
