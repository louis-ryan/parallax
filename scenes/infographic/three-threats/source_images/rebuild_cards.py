from PIL import Image, ImageOps

CANVAS = (1920, 1080)
MAX_ICON_SIZE = 380

def crop_to_content(im):
    bbox = im.getbbox()
    return im.crop(bbox)

def build_card(icon_name, out_name):
    card = Image.open("card_backing.png").convert("RGBA")
    card_bbox = card.getbbox()
    card_cx = (card_bbox[0] + card_bbox[2]) // 2
    card_cy = (card_bbox[1] + card_bbox[3]) // 2

    icon = Image.open(f"{icon_name}.png").convert("RGBA")
    icon = crop_to_content(icon)

    scale = min(MAX_ICON_SIZE / icon.width, MAX_ICON_SIZE / icon.height)
    new_size = (int(icon.width * scale), int(icon.height * scale))
    icon_r = icon.resize(new_size, Image.LANCZOS)

    canvas = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas.paste(card, (0, 0), card)
    x = card_cx - new_size[0] // 2
    y = card_cy - new_size[1] // 2
    canvas.paste(icon_r, (x, y), icon_r)
    canvas.save(f"{out_name}.png")

    bw_icon = ImageOps.grayscale(icon_r.convert("RGB"))
    bw_icon = bw_icon.convert("RGBA")
    bw_icon.putalpha(icon_r.split()[3])

    bw_card = ImageOps.grayscale(card.convert("RGB")).convert("RGBA")
    bw_card.putalpha(card.split()[3])

    canvas_bw = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    canvas_bw.paste(bw_card, (0, 0), bw_card)
    canvas_bw.paste(bw_icon, (x, y), bw_icon)
    canvas_bw.save(f"{out_name}_bw.png")

build_card("icon_nuclear", "card_icon_nuclear")
build_card("icon_climate", "card_icon_climate")
build_card("icon_ai", "card_icon_ai")

print("done")
