#!/usr/bin/env python3
"""
Procedural placeholder art for scenes/inferno/satan-bound.
Bosch-inspired earth cross-section: sky/land sliver -> ground -> earth strata
descent -> hell cavern with bound Satan, demons, fire.

This is a stylized/abstract PLACEHOLDER (gradients + noise + hand-drawn shapes),
not painterly Bosch-level detail -- meant to get a correctly structured layer
stack into the FCPXML pipeline, replaceable later with real painted art.

Outputs (1920x1080, plus oversized canvases where noted for parallax headroom):
  background.png    - opaque: sky, land, strata, hell back wall, Satan+demon silhouettes
  fire.png           - alpha: flame shapes in the hell cavern, for `add` blend + flicker
  smoke.png          - alpha: soft smoke blobs, for `screen`/`add` blend + upward drift
"""
import random
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

random.seed(42)
np.random.seed(42)

W, H = 1920, 1080
OUT = "/Users/louisryan/Desktop/parallax/scenes/inferno/satan-bound/source_images"

# ---------------------------------------------------------------------------
# Vertical layout (deep cross-section framing, per brief)
# ---------------------------------------------------------------------------
SKY_TOP = 0
SKY_BOTTOM = int(H * 0.10)          # thin sky sliver
LAND_BOTTOM = int(H * 0.155)        # land surface strip
GROUND_LINE = LAND_BOTTOM           # boundary between surface and earth
STRATA_BOTTOM = int(H * 0.55)       # earth strata descent ends
HELL_TOP = STRATA_BOTTOM            # hell cavern begins
HELL_BOTTOM = H

CENTER_X = W // 2

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))

# ---------------------------------------------------------------------------
# Background: sky -> land -> strata -> hell, one continuous graded image
# ---------------------------------------------------------------------------
def build_background():
    img = Image.new("RGB", (W, H), (0, 0, 0))
    px = img.load()

    # Color stops (y-fraction -> RGB), Bosch-leaning: washed daylight up top,
    # muddy strata descending, black-brown/fire palette in hell.
    stops = [
        (0.00, (150, 185, 210)),   # pale sky
        (0.09, (190, 205, 200)),   # sky near horizon, hazy
        (0.10, (110, 125, 80)),    # land surface, dull green-brown
        (0.155, (90, 75, 55)),     # topsoil
        (0.22, (95, 78, 55)),      # stratum 1 - ochre brown
        (0.30, (70, 58, 48)),      # stratum 2 - grey-brown
        (0.38, (60, 45, 40)),      # stratum 3 - warming
        (0.46, (55, 32, 28)),      # stratum 4 - deep rust
        (0.55, (60, 24, 16)),      # approaching hell - hot rust
        (0.62, (58, 22, 14)),      # hell back wall - warm charcoal, lit
        (0.80, (46, 16, 12)),      # deep hell, still warm
        (1.00, (30, 10, 8)),       # bottom - dark but not black
    ]

    for y in range(H):
        t = y / H
        # find bracketing stops
        for i in range(len(stops) - 1):
            y0, c0 = stops[i]
            y1, c1 = stops[i + 1]
            if y0 <= t <= y1:
                local_t = 0 if y1 == y0 else (t - y0) / (y1 - y0)
                color = lerp_color(c0, c1, local_t)
                break
        else:
            color = stops[-1][1]
        for x in range(0, W, 4):
            for dx in range(4):
                if x + dx < W:
                    px[x + dx, y] = color

    return img

def add_noise_texture(img, strength=10, region=None):
    arr = np.array(img).astype(np.int16)
    noise = np.random.randint(-strength, strength + 1, arr.shape[:2])
    if region:
        y0, y1 = region
        mask = np.zeros(arr.shape[:2], dtype=bool)
        mask[y0:y1, :] = True
        noise = noise * mask
    for c in range(3):
        arr[:, :, c] = np.clip(arr[:, :, c] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def draw_clouds(img):
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(6):
        cx = random.randint(0, W)
        cy = random.randint(10, SKY_BOTTOM - 15)
        for _ in range(5):
            rx = random.randint(30, 70)
            ry = random.randint(10, 20)
            ox = cx + random.randint(-60, 60)
            oy = cy + random.randint(-8, 8)
            draw.ellipse([ox - rx, oy - ry, ox + rx, oy + ry],
                         fill=(235, 235, 230, 60))
    return img

def draw_land_detail(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # a few sparse trees/rocks as tiny dark silhouettes on the land strip
    for _ in range(14):
        x = random.randint(0, W)
        y = random.randint(LAND_BOTTOM - 14, LAND_BOTTOM - 4)
        h = random.randint(6, 14)
        draw.polygon([(x, y + h), (x - 3, y), (x + 3, y)], fill=(40, 45, 25, 200))
    # thin ground line
    draw.line([(0, GROUND_LINE), (W, GROUND_LINE)], fill=(20, 15, 10, 180), width=2)
    return img

def draw_strata_lines(img):
    draw = ImageDraw.Draw(img, "RGBA")
    y = LAND_BOTTOM
    while y < STRATA_BOTTOM:
        y += random.randint(28, 55)
        if y >= STRATA_BOTTOM:
            break
        wobble_pts = []
        for x in range(0, W + 40, 40):
            wobble_pts.append((x, y + random.randint(-6, 6)))
        draw.line(wobble_pts, fill=(0, 0, 0, 40), width=2)
        # occasional embedded rock/boulder shape
        if random.random() < 0.5:
            rx = random.randint(0, W)
            ry = y + random.randint(-10, 10)
            rw = random.randint(20, 50)
            draw.ellipse([rx - rw, ry - rw * 0.6, rx + rw, ry + rw * 0.6],
                         fill=(0, 0, 0, 30))
    return img

def draw_roots_and_cracks(img):
    """Glowing lava veins that widen and brighten toward hell."""
    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base, "RGBA")
    for _ in range(7):
        x = random.randint(int(W * 0.12), int(W * 0.88))
        y = STRATA_BOTTOM
        pts = [(x, y)]
        cur_x, cur_y = x, y
        while cur_y > LAND_BOTTOM + 30:
            cur_y -= random.randint(20, 45)
            cur_x += random.randint(-18, 18)
            pts.append((cur_x, cur_y))
        span = STRATA_BOTTOM - LAND_BOTTOM
        for i in range(len(pts) - 1):
            depth_t = 1 - (y - pts[i][1]) / span  # 1 near hell, 0 near surface
            w = max(2, int(9 * depth_t))
            core = (255, int(120 + 60 * depth_t), int(30 * depth_t), int(160 * depth_t + 40))
            draw.line([pts[i], pts[i + 1]], fill=core, width=w)
    glow = base.filter(ImageFilter.GaussianBlur(5))
    combined = Image.alpha_composite(glow, base)
    img = Image.alpha_composite(img.convert("RGBA"), combined).convert("RGB")
    return img

# ---------------------------------------------------------------------------
# Hell cavern back wall detail: cavern silhouette, distant fire glow shape
# ---------------------------------------------------------------------------
def draw_cavern_silhouette(img):
    draw = ImageDraw.Draw(img, "RGBA")
    # jagged cavern roofline at HELL_TOP
    pts = [(0, HELL_TOP)]
    x = 0
    while x < W:
        x += random.randint(40, 90)
        pts.append((min(x, W), HELL_TOP + random.randint(-18, 30)))
    pts.append((W, HELL_TOP))
    draw.polygon(pts, fill=(15, 5, 6, 255))

    # stalactites hanging down
    x = 20
    while x < W:
        x += random.randint(50, 110)
        length = random.randint(20, 60)
        width = random.randint(8, 18)
        draw.polygon([
            (x - width, HELL_TOP + 10),
            (x + width, HELL_TOP + 10),
            (x, HELL_TOP + 10 + length),
        ], fill=(12, 4, 5, 255))
    return img

# ---------------------------------------------------------------------------
# Demons: small grotesque hybrid silhouettes scattered through the hell cavern
# ---------------------------------------------------------------------------
def draw_demon(draw, x, y, scale=1.0, facing=1):
    """A crude horned bipedal demon silhouette, dark, rim-lit by fire glow behind it."""
    s = scale
    body_color = (12, 5, 5, 255)
    rim = (255, 140, 50, 200)
    rim_w = max(1, int(1.5 * s))

    def rim_line(p1, p2, width):
        draw.line([p1, p2], fill=rim, width=width + rim_w * 2)

    def body_line(p1, p2, width):
        draw.line([p1, p2], fill=body_color, width=width)

    leg_pts = [((x, y), (x - 6 * s * facing, y + 22 * s)),
               ((x, y), (x + 6 * s * facing, y + 22 * s))]
    for p1, p2 in leg_pts:
        rim_line(p1, p2, int(4 * s))
    for p1, p2 in leg_pts:
        body_line(p1, p2, int(4 * s))

    # torso (hunched) with rim outline
    torso_box = [x - 9 * s, y - 20 * s, x + 9 * s, y + 4 * s]
    draw.ellipse([b + (rim_w * (-1 if i < 2 else 1)) for i, b in enumerate(torso_box)],
                 fill=rim)
    draw.ellipse(torso_box, fill=body_color)

    # head
    hx, hy = x + 3 * s * facing, y - 26 * s
    head_box = [hx - 6 * s, hy - 6 * s, hx + 6 * s, hy + 6 * s]
    draw.ellipse([b + (rim_w * (-1 if i < 2 else 1)) for i, b in enumerate(head_box)],
                 fill=rim)
    draw.ellipse(head_box, fill=body_color)

    # horns
    horn_pts = [((hx - 3 * s, hy - 5 * s), (hx - 7 * s, hy - 14 * s)),
                ((hx + 3 * s, hy - 5 * s), (hx + 7 * s, hy - 14 * s))]
    for p1, p2 in horn_pts:
        rim_line(p1, p2, int(2 * s))
    for p1, p2 in horn_pts:
        body_line(p1, p2, int(2 * s))

    # glowing eyes
    draw.ellipse([hx - 3 * s, hy - 1 * s, hx - 1 * s, hy + 1 * s], fill=(255, 160, 40, 255))
    draw.ellipse([hx + 1 * s, hy - 1 * s, hx + 3 * s, hy + 1 * s], fill=(255, 160, 40, 255))

    # arm reaching/gesturing
    arm = ((x - 8 * s, y - 14 * s), (x - 20 * s * facing, y - 22 * s))
    rim_line(*arm, int(3 * s))
    body_line(*arm, int(3 * s))

    # tail
    tail_pts = [(x, y + 2 * s)]
    tx, ty = x, y + 2 * s
    for i in range(4):
        tx -= 5 * s * facing
        ty += random.uniform(-3, 3) * s
        tail_pts.append((tx, ty))
    draw.line(tail_pts, fill=rim, width=int(2 * s) + rim_w * 2)
    draw.line(tail_pts, fill=body_color, width=int(2 * s))

DEMON_POSITIONS = [
    (280, 800, 2.2, 1), (430, 920, 1.8, -1), (1520, 810, 2.1, -1),
    (1680, 930, 1.7, 1), (700, 960, 1.6, 1), (1230, 960, 1.6, -1),
    (220, 1000, 1.7, 1), (1750, 1010, 1.8, -1), (900, 1040, 1.4, 1),
    (1060, 1040, 1.4, -1),
]

def draw_demon_glow(glow_img, x, y, scale):
    gdraw = ImageDraw.Draw(glow_img, "RGBA")
    r = 55 * scale
    gdraw.ellipse([x - r, y - r * 1.3, x + r, y + r * 0.5],
                  fill=(255, 130, 40, 130))

def draw_demons(img):
    img = img.convert("RGBA")
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for x, y, sc, f in DEMON_POSITIONS:
        draw_demon_glow(glow, x, y, sc)
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img, "RGBA")
    for x, y, sc, f in DEMON_POSITIONS:
        draw_demon(draw, x, y, sc, f)
    return img.convert("RGB")

# ---------------------------------------------------------------------------
# Satan: larger bound figure at center of the hell cavern
# ---------------------------------------------------------------------------
def draw_satan(img):
    img = img.convert("RGBA")
    cx, cy = CENTER_X, int(H * 0.82)

    # strong glow behind Satan so his silhouette rim-lights against it
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([cx - 320, cy - 260, cx + 320, cy + 260], fill=(255, 140, 50, 200))
    gdraw.ellipse([cx - 180, cy - 160, cx + 180, cy + 160], fill=(255, 190, 90, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(55))
    img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img, "RGBA")
    color = (10, 4, 5, 255)
    outline = (255, 150, 60, 230)

    scale = 2.6
    rim_w = 6

    def rim_line(p1, p2, width):
        draw.line([p1, p2], fill=outline, width=width + rim_w * 2)

    def body_line(p1, p2, width):
        draw.line([p1, p2], fill=color, width=width)

    def rim_polygon(pts, pad=rim_w):
        cxp = sum(p[0] for p in pts) / len(pts)
        cyp = sum(p[1] for p in pts) / len(pts)
        expanded = []
        for px, py in pts:
            dx, dy = px - cxp, py - cyp
            dist = max(1, (dx ** 2 + dy ** 2) ** 0.5)
            expanded.append((px + dx / dist * pad, py + dy / dist * pad))
        draw.polygon(expanded, fill=outline)

    # wings, folded/broken behind (drawn first, further back)
    left_wing = [
        (cx - 24 * scale, cy - 5 * scale),
        (cx - 70 * scale, cy - 30 * scale),
        (cx - 55 * scale, cy + 30 * scale),
        (cx - 26 * scale, cy + 30 * scale),
    ]
    right_wing = [
        (cx + 24 * scale, cy - 5 * scale),
        (cx + 70 * scale, cy - 30 * scale),
        (cx + 55 * scale, cy + 30 * scale),
        (cx + 26 * scale, cy + 30 * scale),
    ]
    rim_polygon(left_wing, pad=8)
    rim_polygon(right_wing, pad=8)
    draw.polygon(left_wing, fill=(5, 2, 3, 235))
    draw.polygon(right_wing, fill=(5, 2, 3, 235))

    # legs, bound together at ankles
    leg1 = ((cx - 20 * scale, cy + 60 * scale), (cx, cy + 100 * scale))
    leg2 = ((cx + 20 * scale, cy + 60 * scale), (cx, cy + 100 * scale))
    rim_line(*leg1, int(9 * scale))
    rim_line(*leg2, int(9 * scale))
    body_line(*leg1, int(9 * scale))
    body_line(*leg2, int(9 * scale))
    # ankle binding
    draw.ellipse([cx - 10 * scale, cy + 94 * scale, cx + 10 * scale, cy + 106 * scale],
                 outline=(200, 160, 60, 255), width=4)

    # arms pulled back and bound behind
    arm1 = ((cx - 22 * scale, cy - 5 * scale), (cx - 40 * scale, cy + 20 * scale))
    arm2 = ((cx + 22 * scale, cy - 5 * scale), (cx + 40 * scale, cy + 20 * scale))
    rim_line(*arm1, int(7 * scale))
    rim_line(*arm2, int(7 * scale))
    body_line(*arm1, int(7 * scale))
    body_line(*arm2, int(7 * scale))

    # torso, hunched/kneeling
    torso = [
        (cx - 26 * scale, cy + 60 * scale),
        (cx - 22 * scale, cy - 10 * scale),
        (cx, cy - 24 * scale),
        (cx + 22 * scale, cy - 10 * scale),
        (cx + 26 * scale, cy + 60 * scale),
    ]
    rim_polygon(torso, pad=8)
    draw.polygon(torso, fill=color)

    # chain/rope binding across chest and wrists
    draw.line([(cx - 38 * scale, cy + 18 * scale), (cx + 38 * scale, cy + 18 * scale)],
              fill=(200, 160, 60, 255), width=5)
    draw.line([(cx - 24 * scale, cy + 5 * scale), (cx + 24 * scale, cy + 5 * scale)],
              fill=(200, 160, 60, 255), width=4)

    # neck + head
    hx, hy = cx, cy - 40 * scale
    head_box = [hx - 13 * scale, hy - 15 * scale, hx + 13 * scale, hy + 12 * scale]
    rim_box = [b - rim_w if i < 2 else b + rim_w for i, b in enumerate(head_box)]
    draw.ellipse(rim_box, fill=outline)
    draw.ellipse(head_box, fill=color)

    # horns, large and curved
    horn1 = ((hx - 7 * scale, hy - 12 * scale), (hx - 22 * scale, hy - 34 * scale))
    horn2 = ((hx + 7 * scale, hy - 12 * scale), (hx + 22 * scale, hy - 34 * scale))
    rim_line(*horn1, int(5 * scale))
    rim_line(*horn2, int(5 * scale))
    body_line(*horn1, int(5 * scale))
    body_line(*horn2, int(5 * scale))

    # glowing eyes
    draw.ellipse([hx - 7 * scale, hy - 2 * scale, hx - 3 * scale, hy + 2 * scale],
                 fill=(255, 180, 60, 255))
    draw.ellipse([hx + 3 * scale, hy - 2 * scale, hx + 7 * scale, hy + 2 * scale],
                 fill=(255, 180, 60, 255))

    # chain anchoring him to the cavern floor
    anchor_y = cy + 106 * scale
    draw.line([(cx, anchor_y), (cx, min(H - 10, anchor_y + 40))],
              fill=(200, 160, 60, 255), width=6)

    return img.convert("RGB")

# ---------------------------------------------------------------------------
# Fire layer (separate alpha PNG, additive blend, flicker source)
# ---------------------------------------------------------------------------
def build_fire_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")

    flame_clusters = [
        (150, 1000, 90), (450, 1050, 70), (750, 1000, 60),
        (1170, 1030, 65), (1470, 1000, 85), (1770, 1040, 70),
        (300, 850, 40), (1620, 860, 40), (960, 1060, 100),
        (60, 700, 30), (1860, 720, 30),
    ]
    for cx, cy, size in flame_clusters:
        for _ in range(random.randint(8, 14)):
            fx = cx + random.randint(-size // 2, size // 2)
            fy = cy + random.randint(-size // 3, size // 3)
            fh = random.randint(int(size * 0.6), size)
            fw = int(fh * random.uniform(0.25, 0.4))
            # flame as tapered polygon
            pts = [
                (fx - fw, fy),
                (fx - fw * 0.4, fy - fh * 0.6),
                (fx, fy - fh),
                (fx + fw * 0.4, fy - fh * 0.6),
                (fx + fw, fy),
            ]
            color = random.choice([
                (255, 100, 20, 255), (255, 160, 30, 240), (255, 210, 70, 210)
            ])
            draw.polygon(pts, fill=color)

    img = img.filter(ImageFilter.GaussianBlur(2))

    # bright core glow behind Satan
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse([CENTER_X - 260, int(H * 0.68), CENTER_X + 260, H + 100],
                  fill=(255, 130, 40, 90))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(glow, img)

    return img

# ---------------------------------------------------------------------------
# Smoke layer (separate alpha PNG, slow upward drift, screen/add blend)
# ---------------------------------------------------------------------------
def build_smoke_layer():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(28):
        cx = random.randint(0, W)
        cy = random.randint(int(H * 0.35), H)
        r = random.randint(60, 160)
        alpha = random.randint(12, 30)
        draw.ellipse([cx - r, cy - r * 0.6, cx + r, cy + r * 0.6],
                     fill=(120, 100, 90, alpha))
    img = img.filter(ImageFilter.GaussianBlur(40))
    return img

# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------
def main():
    bg = build_background()
    bg = draw_clouds(bg)
    bg = draw_land_detail(bg)
    bg = draw_strata_lines(bg)
    bg = draw_roots_and_cracks(bg)
    bg = draw_cavern_silhouette(bg)
    bg = draw_demons(bg)
    bg = draw_satan(bg)
    bg = add_noise_texture(bg, strength=8)
    bg = bg.filter(ImageFilter.GaussianBlur(0.6))
    bg = ImageEnhance.Color(bg).enhance(1.15)
    bg = ImageEnhance.Contrast(bg).enhance(1.1)
    bg.save(f"{OUT}/background.png")
    print("saved background.png", bg.size)

    fire = build_fire_layer()
    fire.save(f"{OUT}/fire.png")
    print("saved fire.png", fire.size)

    smoke = build_smoke_layer()
    smoke.save(f"{OUT}/smoke.png")
    print("saved smoke.png", smoke.size)

if __name__ == "__main__":
    main()
