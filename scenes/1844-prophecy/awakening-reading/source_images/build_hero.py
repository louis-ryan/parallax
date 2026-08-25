from PIL import Image, ImageFilter

CANVAS = (1920, 1080)

def build_clean_hero(image_path, out_name, piece_w, piece_h, feather=90):
    img = Image.open(image_path).convert("RGB")
    src_w, src_h = img.size
    src_ratio = src_w / src_h
    dst_ratio = piece_w / piece_h
    if src_ratio > dst_ratio:
        new_h = src_h
        new_w = int(new_h * dst_ratio)
        x0 = (src_w - new_w) // 2
        y0 = 0
    else:
        new_w = src_w
        new_h = int(new_w / dst_ratio)
        x0 = 0
        y0 = (src_h - new_h) // 2
    img = img.crop((x0, y0, x0 + new_w, y0 + new_h)).resize((piece_w, piece_h), Image.LANCZOS)

    # feathered rectangular alpha mask (soft edge fade, no hard photo-crop line, no
    # torn-paper card this time — this scene's hero sits directly on the geometric
    # backdrop as a glowing photographic vignette, not a paper-cutout piece)
    mask = Image.new("L", (piece_w, piece_h), 0)
    from PIL import ImageDraw
    d = ImageDraw.Draw(mask)
    d.rectangle([feather, feather, piece_w - feather, piece_h - feather], fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(feather * 0.6))

    piece = Image.new("RGBA", (piece_w, piece_h), (0, 0, 0, 0))
    piece.paste(img, (0, 0))
    piece.putalpha(mask)

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    ox = (CANVAS[0] - piece_w) // 2
    oy = (CANVAS[1] - piece_h) // 2
    canvas.paste(piece, (ox, oy), piece)
    canvas.save(f"{out_name}.png")

    wick_frac_x, wick_frac_y = 0.789, 0.11
    wick_src_x = wick_frac_x * src_w
    wick_src_y = wick_frac_y * src_h
    in_crop = (x0 <= wick_src_x <= x0 + new_w) and (y0 <= wick_src_y <= y0 + new_h)
    local_x = wick_src_x - x0
    local_y = wick_src_y - y0
    scale = piece_w / new_w
    wick_piece_x = local_x * scale
    wick_piece_y = local_y * scale
    wick_canvas_x = ox + wick_piece_x
    wick_canvas_y = oy + wick_piece_y
    print("wick in crop:", in_crop)
    print("wick absolute canvas position:", wick_canvas_x, wick_canvas_y)
    print("wick offset from canvas center (960,540):", wick_canvas_x - 960, wick_canvas_y - 540)


build_clean_hero("hero_bible_candle.jpg", "piece_hero_bible", 880, 700)
print("done")
