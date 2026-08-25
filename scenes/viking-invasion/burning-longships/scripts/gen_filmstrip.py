#!/usr/bin/env python3
"""Comic-book-style filmstrip preview for burning-longships.

Parses burning_longships.fcpxml directly (not hardcoded values) to find each
layer's adjust-transform keyframes, interpolates 5 evenly-spaced timestamps,
undoes the /10.8 hand-authored-position correction (methodology.md #2) to work
in real pixel space, and composites the locally-available source_images layers
with PIL. The universal paper-texture overlay and reused lightning.mov aren't
depicted (no local source image for either in this headless checkout) — noted
in the output caption.

Run: python3 scripts/gen_filmstrip.py
"""
import xml.etree.ElementTree as ET
from PIL import Image

FCPXML = "burning_longships.fcpxml"
DURATION = 20.0
SAMPLE_TIMES = [0.0, 5.0, 10.0, 15.0, 20.0]
CANVAS = (1920, 1080)
PANEL_W = 380
PANEL_H = round(PANEL_W * CANVAS[1] / CANVAS[0])
GAP = 4

# maps asset id -> local source_images filename (only layers we can actually
# render from a still PNG in this headless checkout)
ASSET_TO_IMAGE = {
    "r3": "source_images/sky_sea_background.png",
    "r6": "source_images/burning_longships.png",
    "r7": "source_images/viking_backs.png",
    "r9": "source_images/embers_overlay.png",
}


def parse_time(t):
    """FCPXML time strings are either 'Ns' or 'N/Ds' rational seconds."""
    t = t.rstrip("s")
    if "/" in t:
        num, den = t.split("/")
        return float(num) / float(den)
    return float(t)


def parse_value_pair(v):
    parts = v.split()
    return (float(parts[0]), float(parts[1])) if len(parts) == 2 else (float(parts[0]), float(parts[0]))


def interp(keyframes, t):
    """keyframes: list of (time, (x,y)). Linear interpolation (good enough for
    a rough preview regardless of the FCPXML curve attribute)."""
    if not keyframes:
        return (0.0, 0.0)
    if t <= keyframes[0][0]:
        return keyframes[0][1]
    if t >= keyframes[-1][0]:
        return keyframes[-1][1]
    for i in range(len(keyframes) - 1):
        t0, v0 = keyframes[i]
        t1, v1 = keyframes[i + 1]
        if t0 <= t <= t1:
            frac = (t - t0) / (t1 - t0) if t1 > t0 else 0
            return (v0[0] + (v1[0] - v0[0]) * frac, v0[1] + (v1[1] - v0[1]) * frac)
    return keyframes[-1][1]


def extract_layers():
    tree = ET.parse(FCPXML)
    root = tree.getroot()
    resources = root.find("resources")
    compound = resources.find("media")
    outer_clip = compound.find(".//spine/asset-clip")

    layers = []

    def read_clip(clip, lane):
        ref = clip.get("ref")
        if ref not in ASSET_TO_IMAGE:
            return None
        transform = clip.find("adjust-transform")
        static_scale = (1.0, 1.0)
        scale_kf, pos_kf = [], []
        if transform is not None:
            if transform.get("scale"):
                static_scale = parse_value_pair(transform.get("scale"))
            for param in transform.findall("param"):
                name = param.get("name")
                kfa = param.find("keyframeAnimation")
                target = scale_kf if name == "scale" else pos_kf if name == "position" else None
                if target is None:
                    continue
                if kfa is not None:
                    for kf in kfa.findall("keyframe"):
                        target.append((parse_time(kf.get("time")), parse_value_pair(kf.get("value"))))
                elif param.get("value"):
                    target.append((0.0, parse_value_pair(param.get("value"))))
        return {
            "lane": lane,
            "ref": ref,
            "image": ASSET_TO_IMAGE[ref],
            "static_scale": static_scale,
            "scale_kf": sorted(scale_kf),
            "pos_kf": sorted(pos_kf),
        }

    bg = read_clip(outer_clip, lane=0)
    if bg:
        layers.append(bg)
    for child in outer_clip.findall("asset-clip"):
        entry = read_clip(child, lane=int(child.get("lane", "0")))
        if entry:
            layers.append(entry)

    layers.sort(key=lambda l: l["lane"])
    return layers


def render_frame(layers, t):
    canvas = Image.new("RGB", CANVAS, (10, 8, 14))
    for layer in layers:
        img = Image.open(layer["image"]).convert("RGBA")

        sx, sy = layer["static_scale"]
        if layer["scale_kf"]:
            sx, sy = interp(layer["scale_kf"], t)
        px, py = interp(layer["pos_kf"], t) if layer["pos_kf"] else (0.0, 0.0)
        # undo the /10.8 hand-authored-position correction -> real pixel space
        px_real, py_real = px * 10.8, py * 10.8

        new_w, new_h = max(1, int(CANVAS[0] * sx)), max(1, int(CANVAS[1] * sy))
        scaled = img.resize((new_w, new_h), Image.BILINEAR)

        # FCP position is a center offset in a y-up coordinate system with
        # (0,0) = frame center.
        cx = CANVAS[0] / 2 + px_real - new_w / 2
        cy = CANVAS[1] / 2 - py_real - new_h / 2
        canvas.paste(scaled, (int(cx), int(cy)), scaled)
    return canvas


def build_filmstrip():
    layers = extract_layers()
    panels = []
    for t in SAMPLE_TIMES:
        frame = render_frame(layers, t)
        panel = frame.resize((PANEL_W, PANEL_H), Image.LANCZOS)
        panels.append(panel)

    total_w = PANEL_W * len(panels) + GAP * (len(panels) - 1)
    strip = Image.new("RGB", (total_w, PANEL_H), (0, 0, 0))
    x = 0
    for panel in panels:
        strip.paste(panel, (x, 0))
        x += PANEL_W + GAP

    strip.save("burning_longships_filmstrip.png")
    print("wrote burning_longships_filmstrip.png", strip.size)


if __name__ == "__main__":
    build_filmstrip()
