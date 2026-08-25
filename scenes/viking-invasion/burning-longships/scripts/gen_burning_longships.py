#!/usr/bin/env python3
"""Procedural source-art generator for viking-invasion/burning-longships.

Produces the 4 source_images/ layers for this scene, following
scenes/viking-invasion/style.md's dusk/storm palette formula (vertical
gradient blended with luminance, pixel-art silhouettes, no photographic
texture) and requirements.md's layer checklist (opaque background, alpha
midground/foreground/atmospheric layers).

Run: python3 scripts/gen_burning_longships.py
"""
import math
import random

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

random.seed(11)
np.random.seed(11)

W, H = 1920, 1080
OUT = "source_images"

# ---------------------------------------------------------------------------
# style.md dusk/storm gradient stops
# ---------------------------------------------------------------------------
STOPS = [
    (0.00, (35, 25, 65)),    # top: deep purple-navy
    (0.42, (180, 70, 90)),   # upper-mid: dramatic pink/magenta
    (0.62, (255, 140, 70)),  # near horizon: fiery warm orange
    (1.00, (60, 50, 80)),    # below horizon/water: cools back down
]


def gradient_column(h):
    """Vertical dusk/storm gradient, h pixels tall, per style.md stops."""
    col = np.zeros((h, 3), dtype=np.float32)
    for y in range(h):
        t = y / (h - 1)
        for i in range(len(STOPS) - 1):
            t0, c0 = STOPS[i]
            t1, c1 = STOPS[i + 1]
            if t0 <= t <= t1:
                local = (t - t0) / (t1 - t0) if t1 > t0 else 0
                col[y] = [c0[j] + (c1[j] - c0[j]) * local for j in range(3)]
                break
        else:
            col[y] = STOPS[-1][1]
    return col


def pixelate(img, factor):
    """Hard-edged pixel-art downsample/upsample."""
    w, h = img.size
    small = img.resize((max(1, w // factor), max(1, h // factor)), Image.BILINEAR)
    return small.resize((w, h), Image.NEAREST)


def add_noise_luminance(base_rgb, w, h, strength=18, seed=0):
    """A cheap 'cloud/terrain detail' luminance layer to blend under the gradient."""
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, 1, (h // 8, w // 8))
    noise_range = noise.max() - noise.min()
    noise_img = Image.fromarray(((noise - noise.min()) / (noise_range + 1e-6) * 255).astype(np.uint8))
    noise_img = noise_img.resize((w, h), Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
    noise_arr = np.asarray(noise_img).astype(np.float32)
    noise_arr = (noise_arr - 128) / 128 * strength
    out = base_rgb.astype(np.float32) + noise_arr[..., None]
    return np.clip(out, 0, 255)


def make_sky_sea_background():
    horizon = int(H * 0.58)

    grad_col = gradient_column(H)
    grad = np.repeat(grad_col[:, None, :], W, axis=1)

    lum_noise = add_noise_luminance(grad, W, H, strength=14, seed=1)
    blended = grad * 0.8 + lum_noise * 0.2

    img = Image.fromarray(np.clip(blended, 0, 255).astype(np.uint8), "RGB")
    img = pixelate(img, 3)

    draw = ImageDraw.Draw(img)

    # storm cloud silhouette bands, upper sky, hard-edged pixel-art shapes
    cloud_color = (28, 20, 45)
    for i in range(6):
        cy = int(H * (0.06 + 0.05 * i)) + random.randint(-10, 10)
        cx0 = random.randint(-100, W // 2)
        cw = random.randint(500, 1100)
        ch = random.randint(30, 70)
        draw.ellipse([cx0, cy, cx0 + cw, cy + ch], fill=cloud_color + (0,) if False else cloud_color)

    # sea band below horizon, slightly darker + banded "wave" texture (large
    # feature wavelength so a full cycle doesn't visibly loop in a 20s pan)
    sea = img.crop((0, horizon, W, H))
    sea_arr = np.asarray(sea).astype(np.float32)
    xs = np.arange(W)
    for band in range(4):
        wavelength = 2600 + band * 300  # > frame width, per methodology.md wave lesson
        amp = 6 - band
        yoff = (np.sin(2 * math.pi * xs / wavelength + band) * amp).astype(np.int32)
        band_y = int((sea_arr.shape[0]) * (0.2 + 0.2 * band))
        for x in range(0, W, 3):
            yy = min(sea_arr.shape[0] - 1, max(0, band_y + yoff[x]))
            sea_arr[yy, x:x + 3] *= 0.88
    sea = Image.fromarray(np.clip(sea_arr, 0, 255).astype(np.uint8), "RGB")
    img.paste(sea, (0, horizon))

    # thin bright horizon line (fire-lit glow reflecting off water)
    draw = ImageDraw.Draw(img)
    for dy in range(-2, 3):
        alpha = 1 - abs(dy) / 3
        draw.line([(0, horizon + dy), (W, horizon + dy)],
                   fill=(255, 170, 90), width=1)

    img = ImageEnhance.Color(img).enhance(1.25)
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img.save(f"{OUT}/sky_sea_background.png")
    print("wrote sky_sea_background.png", img.size)
    return horizon


def draw_longship(draw, cx, base_y, scale, ablaze, flame_phase):
    """A dragon-prowed longship silhouette, optionally ablaze."""
    hull_w = int(340 * scale)
    hull_h = int(46 * scale)
    hull = [
        (cx - hull_w // 2, base_y),
        (cx - hull_w // 2 + 20 * scale, base_y - hull_h),
        (cx + hull_w // 2 - 20 * scale, base_y - hull_h),
        (cx + hull_w // 2, base_y),
        (cx + hull_w // 2 - 30 * scale, base_y + hull_h * 0.4),
        (cx - hull_w // 2 + 30 * scale, base_y + hull_h * 0.4),
    ]
    hull_color = (18, 14, 22, 255) if not ablaze else (30, 16, 14, 255)
    draw.polygon(hull, fill=hull_color)

    # dragon-head prow, curling up at the bow (right end)
    prow_x = cx + hull_w // 2
    prow = [
        (prow_x - 10 * scale, base_y - hull_h * 0.6),
        (prow_x + 34 * scale, base_y - hull_h * 1.9),
        (prow_x + 46 * scale, base_y - hull_h * 1.6),
        (prow_x + 20 * scale, base_y - hull_h * 0.4),
    ]
    draw.polygon(prow, fill=hull_color)

    # shield row along the hull side
    n_shields = max(3, int(hull_w / (34 * scale)))
    for i in range(n_shields):
        sx = cx - hull_w // 2 + 24 * scale + i * (hull_w - 48 * scale) / max(1, n_shields - 1)
        sy = base_y - hull_h * 0.35
        r = 9 * scale
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=hull_color)

    # mast (may be a broken stub if ablaze)
    mast_x = cx - hull_w * 0.05
    mast_top = base_y - hull_h - (200 * scale if not ablaze else 70 * scale)
    draw.line([(mast_x, base_y - hull_h), (mast_x, mast_top)], fill=hull_color, width=max(2, int(4 * scale)))

    if ablaze:
        flame_base_y = base_y - hull_h * 0.7
        for i in range(10):
            fx = cx - hull_w // 2 + 20 * scale + i * (hull_w - 40 * scale) / 9
            fh = (60 + 50 * abs(math.sin(flame_phase + i * 1.3))) * scale
            fw = (18 + 8 * math.cos(flame_phase * 1.7 + i)) * scale
            flame = [
                (fx - fw / 2, flame_base_y),
                (fx - fw / 4, flame_base_y - fh * 0.6),
                (fx, flame_base_y - fh),
                (fx + fw / 4, flame_base_y - fh * 0.55),
                (fx + fw / 2, flame_base_y),
            ]
            outer = (255, 120, 30, 235)
            inner_h = fh * 0.55
            inner = [
                (fx - fw / 4, flame_base_y),
                (fx, flame_base_y - inner_h),
                (fx + fw / 4, flame_base_y),
            ]
            draw.polygon(flame, fill=outer)
            draw.polygon(inner, fill=(255, 210, 90, 235))

        # smoke column, soft dark shapes drifting up (blurred afterward)
        for i in range(5):
            sx = cx + random.randint(-int(60 * scale), int(60 * scale))
            sy = flame_base_y - fh - i * 55 * scale
            r = (30 + i * 10) * scale
            draw.ellipse([sx - r, sy - r * 0.7, sx + r, sy + r * 0.7], fill=(40, 36, 40, int(150 - i * 20)))


def make_burning_longships(horizon):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    base_y = horizon + 10
    draw_longship(draw, int(W * 0.36), base_y, 1.35, ablaze=True, flame_phase=0.3)
    draw_longship(draw, int(W * 0.68), base_y - 6, 1.05, ablaze=True, flame_phase=1.8)

    img = img.filter(ImageFilter.GaussianBlur(1))  # settle hard pixel edges slightly
    img.save(f"{OUT}/burning_longships.png")
    print("wrote burning_longships.png", img.size)


def draw_viking(draw, cx, base_y, scale, horned):
    """A Viking silhouette seen from behind: head, torso, legs."""
    head_r = int(16 * scale)
    head_cy = base_y - int(150 * scale)
    draw.ellipse([cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r], fill=(8, 6, 10, 255))

    if horned:
        for side in (-1, 1):
            hx = cx + side * head_r * 0.8
            hy = head_cy - head_r * 0.6
            horn = [
                (hx, hy),
                (hx + side * 22 * scale, hy - 26 * scale),
                (hx + side * 10 * scale, hy - 4 * scale),
            ]
            draw.polygon(horn, fill=(8, 6, 10, 255))

    shoulder_w = int(46 * scale)
    torso_top = head_cy + head_r * 0.7
    torso_bottom = base_y - int(55 * scale)
    torso = [
        (cx - shoulder_w, torso_top),
        (cx + shoulder_w, torso_top),
        (cx + shoulder_w * 0.7, torso_bottom),
        (cx - shoulder_w * 0.7, torso_bottom),
    ]
    draw.polygon(torso, fill=(8, 6, 10, 255))

    # a raised spear/axe silhouette on roughly a third of the figures
    if random.random() < 0.33:
        draw.line([(cx + shoulder_w * 0.6, torso_top), (cx + shoulder_w * 1.4, head_cy - head_r * 3)],
                   fill=(8, 6, 10, 255), width=max(2, int(3 * scale)))

    leg_w = int(16 * scale)
    for side in (-1, 1):
        lx = cx + side * leg_w
        draw.line([(lx, torso_bottom), (lx + side * 4, base_y)], fill=(8, 6, 10, 255), width=max(3, int(10 * scale)))


def make_viking_backs():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    base_y = int(H * 0.97)
    xs = np.linspace(W * 0.04, W * 0.96, 11)
    for i, x in enumerate(xs):
        jitter_x = random.randint(-18, 18)
        scale = random.uniform(1.5, 2.1)
        by = base_y - random.randint(0, 30)
        draw_viking(draw, int(x + jitter_x), by, scale, horned=(i % 3 == 0))

    img.save(f"{OUT}/viking_backs.png")
    print("wrote viking_backs.png", img.size)


def make_embers_overlay():
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for _ in range(140):
        x = random.uniform(W * 0.15, W * 0.9)
        y = random.uniform(H * 0.35, H * 0.95)
        r = random.uniform(1.2, 3.5)
        heat = random.random()
        color = (255, int(140 + 90 * heat), int(40 + 60 * heat), random.randint(120, 220))
        draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
        if random.random() < 0.3:
            r2 = r * 2.2
            glow = (255, int(150 + 80 * heat), 60, 60)
            draw.ellipse([x - r2, y - r2, x + r2, y + r2], fill=glow)

    img = img.filter(ImageFilter.GaussianBlur(0.6))
    img.save(f"{OUT}/embers_overlay.png")
    print("wrote embers_overlay.png", img.size)


if __name__ == "__main__":
    horizon = make_sky_sea_background()
    make_burning_longships(horizon)
    make_viking_backs()
    make_embers_overlay()
