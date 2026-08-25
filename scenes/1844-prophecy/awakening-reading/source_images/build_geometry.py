import math
from PIL import Image, ImageDraw, ImageFilter

CANVAS = (1920, 1080)
CX, CY = CANVAS[0] // 2, CANVAS[1] // 2 - 60

def make_radiating_lines(out_name, n=28, inner_r=180, outer_r=1400, color=(210, 170, 90, 60)):
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for i in range(n):
        angle = (2 * math.pi * i) / n
        x1 = CX + inner_r * math.cos(angle)
        y1 = CY + inner_r * math.sin(angle)
        x2 = CX + outer_r * math.cos(angle)
        y2 = CY + outer_r * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=2)
    canvas = canvas.filter(ImageFilter.GaussianBlur(1.0))
    canvas.save(f"{out_name}.png")

def make_concentric_rings(out_name, radii, color=(190, 150, 80, 90), width=2):
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for r in radii:
        draw.ellipse([CX - r, CY - r, CX + r, CY + r], outline=color, width=width)
    canvas = canvas.filter(ImageFilter.GaussianBlur(0.8))
    canvas.save(f"{out_name}.png")

def make_triangle_field(out_name, seed_positions, color=(200, 160, 85, 55)):
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    for (x, y, s, rot) in seed_positions:
        pts = []
        for k in range(3):
            a = rot + (2 * math.pi * k) / 3
            pts.append((x + s * math.cos(a), y + s * math.sin(a)))
        draw.polygon(pts, outline=color, width=2)
    canvas = canvas.filter(ImageFilter.GaussianBlur(0.6))
    canvas.save(f"{out_name}.png")

def make_vignette_glow(out_name, radius=650, color=(255, 210, 130, 80)):
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse([CX - radius, CY - radius, CX + radius, CY + radius], fill=color)
    canvas = canvas.filter(ImageFilter.GaussianBlur(220))
    canvas.save(f"{out_name}.png")


make_vignette_glow("geo_glow")
make_radiating_lines("geo_rays")
make_concentric_rings("geo_rings", radii=[260, 420, 620, 880])
make_triangle_field(
    "geo_triangles",
    seed_positions=[
        (420, 260, 90, 0.3),
        (1500, 300, 70, 1.1),
        (300, 820, 60, 2.0),
        (1620, 800, 100, 0.7),
        (960, 140, 50, 1.6),
    ],
)

print("done")
