import math
from PIL import Image, ImageDraw, ImageFilter

CANVAS = (1920, 1080)

def poly(draw, pts, fill):
    draw.polygon(pts, fill=fill)

def make_desk_scene(out_name):
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # WALL — back plane, flat dark warm tone, slightly lighter than pure black
    poly(draw, [(0, 0), (1920, 0), (1920, 640), (0, 640)], (32, 26, 20, 255))

    # WINDOW — faceted arch shape on the wall, upper-left, deep blue-black (night)
    win_pts = [
        (220, 90), (420, 60), (560, 110), (600, 260),
        (560, 420), (420, 470), (240, 440), (170, 280),
    ]
    poly(draw, win_pts, (18, 22, 34, 255))
    # window panes — a couple of thin mullion lines
    draw.line([(220, 90), (240, 440)], fill=(50, 42, 30, 255), width=6)
    draw.line([(560, 110), (560, 420)], fill=(50, 42, 30, 255), width=6)
    draw.line([(170, 280), (600, 260)], fill=(50, 42, 30, 255), width=6)
    # faint moonlit facets inside window
    poly(draw, [(260, 150), (420, 130), (440, 260), (280, 280)], (34, 40, 58, 180))

    # BOOKSHELF — angular stacked-rectangle silhouette, upper-right
    shelf_x0, shelf_y0 = 1420, 40
    shelf_w, shelf_h = 420, 480
    poly(draw, [
        (shelf_x0, shelf_y0), (shelf_x0 + shelf_w, shelf_y0 + 30),
        (shelf_x0 + shelf_w, shelf_y0 + shelf_h), (shelf_x0, shelf_y0 + shelf_h - 20),
    ], (26, 20, 15, 255))
    # book spines — thin vertical facets of varying muted warm tones
    book_colors = [
        (70, 40, 30, 255), (55, 45, 25, 255), (60, 30, 25, 255),
        (45, 38, 28, 255), (65, 42, 22, 255), (50, 32, 24, 255),
    ]
    bx = shelf_x0 + 25
    for i, c in enumerate(book_colors):
        bw = 42
        poly(draw, [
            (bx, shelf_y0 + 45), (bx + bw, shelf_y0 + 48),
            (bx + bw, shelf_y0 + shelf_h - 45), (bx, shelf_y0 + shelf_h - 48),
        ], c)
        bx += bw + 6

    # DESK SURFACE — large flat-shaded trapezoid, angled for a slight top-down
    # perspective (wider at front/bottom, narrower toward the back wall)
    desk_top = [(0, 640), (1920, 640), (1750, 760), (170, 760)]
    poly(draw, desk_top, (58, 42, 28, 255))
    desk_front = [(170, 760), (1750, 760), (1920, 1080), (0, 1080)]
    poly(draw, desk_front, (40, 28, 18, 255))
    # desk front panel facets for a paneled-wood look
    for fx in range(80, 1900, 340):
        poly(draw, [
            (fx, 780), (fx + 260, 780), (fx + 280, 1060), (fx - 20, 1060),
        ], (34, 24, 15, 200))

    # DESK EDGE HIGHLIGHT — thin lighter line along the front desk edge, catching
    # candlelight
    draw.line([(170, 760), (1750, 760)], fill=(110, 80, 45, 160), width=4)

    canvas.save(f"{out_name}.png")


def make_desk_glow_mask(out_name):
    # a soft warm glow pool on the desk surface roughly where the candle sits,
    # to be additively blended so the desk reads as candlelit, not flat-shaded
    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    draw.ellipse([760, 620, 1560, 980], fill=(255, 180, 90, 90))
    canvas = canvas.filter(ImageFilter.GaussianBlur(90))
    canvas.save(f"{out_name}.png")


make_desk_scene("desk_scene")
make_desk_glow_mask("desk_glow")
print("done")
