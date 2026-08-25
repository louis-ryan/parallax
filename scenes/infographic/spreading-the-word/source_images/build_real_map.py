#!/usr/bin/env python3
"""
Real US outline for scenes/infographic/spreading-the-word, replacing the
earlier hand-plotted approximation. Uses actual state boundary geometry
(public domain, via PublicaMundi/MappingAPI's us-states.json, itself derived
from US Census TIGER/Line data), merged into a single continental-US
silhouette and rasterized in the same torn-paper-card style as the rest of
the infographic project.

Excludes Alaska, Hawaii, DC, and Puerto Rico -- the scene depicts a
nineteenth-century doomsday prophecy spreading by newspaper, and none of
those were US states/territory in that period; only the 48 contiguous
states are geographically/historically appropriate here.
"""
import json
import random, math
from PIL import Image, ImageDraw, ImageFilter
from shapely.geometry import shape
from shapely.ops import unary_union

random.seed(5)
CANVAS = (1920, 1080)
OUT = "/Users/louisryan/Desktop/parallax/scenes/infographic/spreading-the-word/source_images"

EXCLUDE = {"Alaska", "Hawaii", "District of Columbia", "Puerto Rico"}

with open(f"{OUT}/data/us_states.json") as f:
    data = json.load(f)

polys = []
for feat in data["features"]:
    name = feat["properties"]["name"]
    if name in EXCLUDE:
        continue
    geom = shape(feat["geometry"])
    polys.append(geom)

merged = unary_union(polys)
print("merged geometry type:", merged.geom_type)

minx, miny, maxx, maxy = merged.bounds
print("bounds:", minx, miny, maxx, maxy)

# Map lon/lat bounds to canvas pixel space, preserving aspect ratio, fit
# within a target box, then we'll composite onto a torn-paper card same as
# every other infographic piece.
TARGET_W, TARGET_H = 1500, 820
geo_w = maxx - minx
geo_h = maxy - miny
scale = min(TARGET_W / geo_w, TARGET_H / geo_h)

def geo_to_px(lon, lat, cx, cy):
    # lat increases northward but pixel y increases downward -> flip
    x = cx + (lon - (minx + maxx) / 2) * scale
    y = cy - (lat - (miny + maxy) / 2) * scale
    return (x, y)


def polygon_rings(geom):
    """Yield (exterior_ring, [hole_rings]) for each polygon in geom (handles
    both Polygon and MultiPolygon)."""
    if geom.geom_type == "Polygon":
        yield geom.exterior.coords, [interior.coords for interior in geom.interiors]
    elif geom.geom_type == "MultiPolygon":
        for part in geom.geoms:
            yield from polygon_rings(part)


def draw_us_map(draw, cx, cy):
    map_color = (200, 178, 140, 255)
    map_edge = (140, 118, 85, 255)

    # Draw each polygon part as filled shape; PIL's ImageDraw doesn't support
    # holes directly, so for any part with interior rings (extremely rare at
    # state-merge scale, e.g. an enclosed lake boundary) we fill the exterior
    # then re-punch the hole using the background/transparent trick: draw the
    # hole in the destination's "erase" pass via a separate mask composite
    # rather than plain polygon fill.
    exteriors = []
    holes = []
    for ext, ints in polygon_rings(merged):
        pts = [geo_to_px(lon, lat, cx, cy) for lon, lat in ext]
        exteriors.append(pts)
        for interior in ints:
            hpts = [geo_to_px(lon, lat, cx, cy) for lon, lat in interior]
            holes.append(hpts)

    for pts in exteriors:
        draw.polygon(pts, fill=map_color, outline=map_edge)

    # Punch any holes (interior rings) back to transparent -- draw them in
    # white on a separate mask and subtract, since ImageDraw can't do
    # even-odd fill natively.
    if holes:
        img_size = draw.im.size if hasattr(draw, "im") else CANVAS
        hole_mask = Image.new("L", img_size, 0)
        hdraw = ImageDraw.Draw(hole_mask)
        for hpts in holes:
            hdraw.polygon(hpts, fill=255)
        # caller will composite this externally; simplest here is to just
        # redraw those regions as transparent isn't possible mid-draw, so we
        # return the hole mask for the caller to apply. In practice this
        # dataset's polygons have no interior rings (verified below), so
        # this path is not expected to trigger.
        return hole_mask
    return None


def paper_card(shape_draw_fn, w, h, seed, fill=(247, 240, 220, 255), shadow_offset=(10, 14)):
    pad = 60
    work_w, work_h = w + pad * 2, h + pad * 2
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))

    card = Image.new("RGBA", (work_w, work_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    cx, cy = work_w / 2, work_h / 2

    rnd = random.Random(seed)
    n = 28
    poly_pts = []
    for i in range(n):
        angle = (2 * math.pi * i) / n
        rx = (w / 2) * (1 + rnd.uniform(-0.05, 0.05))
        ry = (h / 2) * (1 + rnd.uniform(-0.05, 0.05))
        poly_pts.append((cx + rx * math.cos(angle), cy + ry * math.sin(angle)))
    draw.polygon(poly_pts, fill=fill)
    draw.polygon(poly_pts, outline=(150, 130, 95, 200))

    hole_mask = shape_draw_fn(draw, cx, cy)

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


# quick check: does this dataset have any interior rings (lake holes etc.)?
has_holes = any(len(ints) > 0 for _, ints in [(g, list(g.interiors)) for g in ([merged] if merged.geom_type == "Polygon" else list(merged.geoms))])
print("has interior rings:", has_holes)

if __name__ == "__main__":
    us_map = paper_card(draw_us_map, 1500, 820, seed=1,
                         fill=(228, 215, 185, 255), shadow_offset=(10, 14))
    us_map.save(f"{OUT}/us_map.png")
    print("saved us_map.png")
