from PIL import Image

CANVAS = (1920, 1080)

def composite(bubble_name, piece_name, out_name):
    bubble = Image.open(f"{bubble_name}.png").convert("RGBA")
    piece = Image.open(f"{piece_name}.png").convert("RGBA")
    canvas = Image.alpha_composite(bubble, piece)
    canvas.save(f"{out_name}.png")

composite("bubble_shape_flagellants", "piece_bubble_flagellants", "thought_flagellants")
composite("bubble_shape_death", "piece_bubble_death", "thought_death")
composite("bubble_shape_danse", "piece_bubble_danse", "thought_danse")
composite("bubble_shape_witch", "piece_bubble_witch", "thought_witch")

print("done")
