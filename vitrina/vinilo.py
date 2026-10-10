"""Arte plano del vinilo frontal: OBREGOM (carnes) + DrQuesos (quesos artesanales)."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).parent / "fonts"

# Paleta
NEGRO = (16, 14, 17)
VINO = (128, 22, 26)
VINO_OSC = (84, 12, 16)
CREMA = (246, 236, 214)
ORO = (214, 170, 78)
AMARILLO = (247, 190, 22)
AMARILLO_OSC = (214, 142, 10)
AZUL = (18, 52, 102)
BLANCO = (255, 255, 255)
ROJO = (210, 24, 32)
CREMA_Q = (248, 238, 216)
CAFE = (42, 24, 16)


def font(name, size):
    f = ImageFont.truetype(str(FONTS / name), size)
    if name.startswith("Oswald"):
        f.set_variation_by_axes([700])
    return f


def text_c(d, xy, s, f, fill, **kw):
    d.text(xy, s, font=f, fill=fill, anchor="mm", **kw)


def estrella(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=fill)


def cabeza_toro(d, cx, cy, s, fill, hueco):
    """Silueta geométrica de cabeza de toro (s = ancho aprox. de la cara)."""
    # Cuernos
    for side in (-1, 1):
        d.polygon([
            (cx + side * s * 0.30, cy - s * 0.30),
            (cx + side * s * 0.95, cy - s * 0.42),
            (cx + side * s * 1.10, cy - s * 0.85),
            (cx + side * s * 1.02, cy - s * 0.38),
            (cx + side * s * 0.55, cy - s * 0.12),
        ], fill=fill)
        # Orejas
        d.polygon([
            (cx + side * s * 0.42, cy - s * 0.18),
            (cx + side * s * 0.86, cy - s * 0.10),
            (cx + side * s * 0.46, cy + s * 0.08),
        ], fill=fill)
    # Cara
    d.polygon([
        (cx - s * 0.48, cy - s * 0.38), (cx + s * 0.48, cy - s * 0.38),
        (cx + s * 0.40, cy + s * 0.30), (cx + s * 0.26, cy + s * 0.62),
        (cx - s * 0.26, cy + s * 0.62), (cx - s * 0.40, cy + s * 0.30),
    ], fill=fill)
    d.rounded_rectangle((cx - s * 0.30, cy + s * 0.42, cx + s * 0.30, cy + s * 0.80),
                        radius=s * 0.16, fill=fill)
    # Ojos y fosas
    for side in (-1, 1):
        d.ellipse((cx + side * s * 0.22 - s * 0.06, cy - s * 0.06,
                   cx + side * s * 0.22 + s * 0.06, cy + s * 0.06), fill=hueco)
        d.ellipse((cx + side * s * 0.13 - s * 0.05, cy + s * 0.58,
                   cx + side * s * 0.13 + s * 0.05, cy + s * 0.68), fill=hueco)


def insignia_obregon(W, H):
    """Escudo de OBREGOM sobre transparente, tamaño W x H."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = W / 2
    arc_r = H * 0.42
    arc_cy = H * 0.50
    body = (W * 0.04, H * 0.42, W * 0.96, H * 0.94)

    # Contorno crema (arco + cuerpo) y relleno vino
    for pad, col in ((14, CREMA), (0, VINO)):
        d.ellipse((cx - arc_r - pad, arc_cy - arc_r - pad, cx + arc_r + pad, arc_cy + arc_r + pad), fill=col)
        d.rounded_rectangle((body[0] - pad, body[1] - pad, body[2] + pad, body[3] + pad),
                            radius=40 + pad, fill=col)
    # Interior negro del arco y franja interna
    d.ellipse((cx - arc_r + 30, arc_cy - arc_r + 30, cx + arc_r - 30, arc_cy + arc_r - 30), fill=NEGRO)
    d.rounded_rectangle((body[0] + 26, body[1] + 26, body[2] - 26, body[3] - 26), radius=26, fill=NEGRO)
    d.rounded_rectangle((body[0] + 40, body[1] + 40, body[2] - 40, body[3] - 40), radius=18,
                        outline=ORO, width=5)

    # Estrellas y toro
    for i, (dx, r) in enumerate(((-110, 26), (0, 40), (110, 26))):
        estrella(d, cx + dx, arc_cy - arc_r + 85 + (0 if i == 1 else 14), r, ORO)
    cabeza_toro(d, cx, arc_cy - arc_r * 0.30, arc_r * 0.36, CREMA, NEGRO)

    # Nombre
    text_c(d, (cx, H * 0.635), "OBREGOM", font("AbrilFatface-Regular.ttf", int(H * 0.235)), CREMA)

    # Cinta "CARNES SELECTAS"
    ry0, ry1 = H * 0.745, H * 0.855
    rx0, rx1 = W * 0.17, W * 0.83
    for side in (-1, 1):
        x_in = rx0 if side < 0 else rx1
        x_out = x_in + side * 70
        d.polygon([(x_in, ry0 + 18), (x_out, ry0 + 18), (x_out + side * -30, (ry0 + ry1) / 2 + 9),
                   (x_out, ry1 + 18), (x_in, ry1 + 18)], fill=VINO_OSC)
    d.rectangle((rx0, ry0, rx1, ry1), fill=VINO)
    d.line((rx0, ry0 + 8, rx1, ry0 + 8), fill=ORO, width=3)
    d.line((rx0, ry1 - 8, rx1, ry1 - 8), fill=ORO, width=3)
    text_c(d, (cx, (ry0 + ry1) / 2 + 3), "CARNES  SELECTAS", font("BebasNeue-Regular.ttf", int(H * 0.115)), CREMA)
    return im


def cuña_queso(d, x, y, s, borde=AZUL):
    """Cuña de queso con agujeros; (x, y) esquina izquierda-abajo, s = ancho."""
    top = [(x, y - s * 0.38), (x + s * 0.62, y - s * 0.70), (x + s, y - s * 0.46), (x + s * 0.40, y - s * 0.16)]
    front = [(x, y - s * 0.38), (x + s * 0.40, y - s * 0.16), (x + s * 0.40, y + s * 0.14), (x, y - s * 0.06)]
    side = [(x + s * 0.40, y - s * 0.16), (x + s, y - s * 0.46), (x + s, y - s * 0.14), (x + s * 0.40, y + s * 0.14)]
    d.polygon(side, fill=AMARILLO, outline=borde, width=8)
    d.polygon(front, fill=AMARILLO_OSC, outline=borde, width=8)
    d.polygon(top, fill=(255, 214, 80), outline=borde, width=8)
    for hx, hy, hr in ((0.62, -0.18, 0.07), (0.82, -0.25, 0.05), (0.75, -0.02, 0.045),
                       (0.17, -0.12, 0.05), (0.27, 0.02, 0.035)):
        d.ellipse((x + s * (hx - hr), y + s * (hy - hr), x + s * (hx + hr), y + s * (hy + hr)),
                  fill=(196, 120, 6))


def insignia_drquesos(W, H):
    """Insignia de DrQuesos sobre transparente, tamaño W x H."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    box = (W * 0.03, H * 0.10, W * 0.97, H * 0.92)
    d.rounded_rectangle((box[0] - 14, box[1] - 14, box[2] + 14, box[3] + 14), radius=90, fill=BLANCO)
    d.rounded_rectangle(box, radius=78, fill=ROJO)
    d.rounded_rectangle((box[0] + 18, box[1] + 18, box[2] - 18, box[3] - 18), radius=62, fill=CREMA_Q)

    # Medallón rojo con la cuña de queso
    mr = H * 0.30
    mcx, mcy = box[0] + mr + 60, (box[1] + box[3]) / 2
    d.ellipse((mcx - mr - 10, mcy - mr - 10, mcx + mr + 10, mcy + mr + 10), fill=BLANCO)
    d.ellipse((mcx - mr, mcy - mr, mcx + mr, mcy + mr), fill=ROJO)
    cuña_queso(d, mcx - mr * 0.72, mcy + mr * 0.42, mr * 1.45, borde=CAFE)

    # Textos
    tx = (mcx + mr + box[2]) / 2 + 10
    text_c(d, (tx, H * 0.42), "DrQuesos", font("Pacifico-Regular.ttf", int(H * 0.25)), CAFE)
    pill = (tx - W * 0.24, H * 0.68, tx + W * 0.24, H * 0.80)
    d.rounded_rectangle(pill, radius=30, fill=ROJO)
    text_c(d, (tx, (pill[1] + pill[3]) / 2 + 2), "QUESOS  ARTESANALES",
           font("BebasNeue-Regular.ttf", int(H * 0.09)), BLANCO)
    return im


def vinilo(W=7360, H=800):
    """Banda completa del frente. Escala 2:1 respecto al panel en la foto (x 320–4000)."""
    im = Image.new("RGBA", (W, H), NEGRO + (255,))
    d = ImageDraw.Draw(im)

    # Fondo: degradado sutil + filetes
    for y in range(H):
        t = y / H
        v = int(10 + 14 * (1 - abs(t - 0.35) * 1.6))
        d.line((0, y, W, y), fill=(v + 4, v, v + 3, 255))
    d.rectangle((0, 18, W, 30), fill=VINO)
    d.rectangle((0, 38, W, 43), fill=ORO)
    d.rectangle((0, H - 43, W, H - 38), fill=ORO)
    d.rectangle((0, H - 30, W, H - 18), fill=VINO)

    # Insignias (centros en coordenadas del vinilo)
    ob = insignia_obregon(1900, 760)
    dq = insignia_drquesos(2050, 640)
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for layer, (cx, cy) in ((ob, (1720, 410)), (dq, (5700, 420))):
        a = layer.split()[-1].point(lambda v: int(v * 0.7))
        blk = Image.new("RGBA", layer.size, (0, 0, 0, 255))
        blk.putalpha(a)
        sombra.alpha_composite(blk, (int(cx - layer.width / 2 + 14), int(cy - layer.height / 2 + 18)))
    im.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(16)))
    im.alpha_composite(ob, (1720 - ob.width // 2, 410 - ob.height // 2))
    im.alpha_composite(dq, (5700 - dq.width // 2, 420 - dq.height // 2))

    # Centro: lema y líneas de producto
    cx = 3700
    text_c(d, (cx, 300), "Frescura y calidad", font("Pacifico-Regular.ttf", 150), CREMA)
    d.line((cx - 640, 430, cx - 120, 430), fill=ORO, width=4)
    d.line((cx + 120, 430, cx + 640, 430), fill=ORO, width=4)
    estrella(d, cx, 430, 30, ORO)
    text_c(d, (cx, 530), "CERDO  ·  RES  ·  POLLO  ·  EMBUTIDOS  ·  MARISCOS",
           font("BebasNeue-Regular.ttf", 92), ORO)
    text_c(d, (cx, 640), "TODOS LOS DÍAS", font("BebasNeue-Regular.ttf", 70), CREMA)

    # Extremos: sellos pequeños de cada marca
    x = 380
    d.ellipse((x - 200, 210, x + 200, 610), fill=VINO, outline=ORO, width=8)
    d.ellipse((x - 170, 240, x + 170, 580), outline=CREMA, width=4)
    text_c(d, (x, 400), "Ob", font("AbrilFatface-Regular.ttf", 210), CREMA)
    for dx in (-60, 0, 60):
        estrella(d, x + dx, 520 - (8 if dx == 0 else 0), 18 if dx else 24, ORO)
    x = W - 330
    d.ellipse((x - 200, 210, x + 200, 610), fill=BLANCO)
    d.ellipse((x - 185, 225, x + 185, 595), fill=ROJO)
    cuña_queso(d, x - 140, 470, 280, borde=CAFE)
    return im


if __name__ == "__main__":
    out = Path(__file__).parent / "salida"
    out.mkdir(exist_ok=True)
    v = vinilo()
    v.convert("RGB").save(out / "vinilo-frontal.png")
    print("ok", v.size)
