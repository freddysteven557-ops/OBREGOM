"""Render del kiosco-isla ObreGom: vitrina refrigerada de diseño con productos reales al vacío.

Uso: python3 vitrina/kiosco.py  ->  vitrina/salida/kiosco-obregom.jpg
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from vinilo import BLANCO, NEGRO, ROJO, font, logo, panel_drquesos, text_c

AQUI = Path(__file__).parent
PROD = AQUI / "marca" / "productos"
W, H = 1720, 1520

# Empaques recortados de las listas de producto (archivo, caja) — solo el empaque, sin precio
RES = [("lista-res.jpg", b) for b in ((40, 240, 280, 610), (310, 240, 540, 610), (580, 240, 810, 610),
                                       (850, 240, 1080, 610), (40, 730, 280, 1060), (850, 730, 1080, 1060))]
CERDO = [("lista-cerdo.jpg", b) for b in ((40, 250, 330, 560), (580, 590, 840, 910), (60, 950, 330, 1240))]
POLLO = [("lista-pollo.jpg", b) for b in ((275, 235, 500, 430), (520, 235, 745, 430), (770, 235, 995, 430))]


def empaque(nombre, caja, alto):
    """Recorta un empaque al vacío y vuelve transparente el fondo blanco de la ficha."""
    a = np.asarray(Image.open(PROD / nombre).convert("RGB").crop(caja)).astype(np.float32)
    alfa = np.clip((252 - a.min(-1)) / 45, 0, 1) * 255
    im = Image.fromarray(np.dstack([a, alfa]).astype(np.uint8), "RGBA")
    return im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS)


def con_sombra(base, im, x, y):
    sombra = Image.new("RGBA", base.size, (0, 0, 0, 0))
    s = Image.new("RGBA", im.size, (0, 0, 0, 170))
    s.putalpha(im.split()[-1].point(lambda v: int(v * 0.65)))
    sombra.alpha_composite(s, (x + 8, y + 10))
    base.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(8)))
    base.alpha_composite(im, (x, y))


def repisa(base, items, x0, x1, piso):
    """Ubica los empaques centrados en la repisa, apoyados sobre `piso`."""
    total = sum(i.width for i in items) + 28 * (len(items) - 1)
    x = x0 + (x1 - x0 - total) // 2
    for im in items:
        con_sombra(base, im, x, piso - im.height)
        x += im.width + 28


def brillo(size, xy, radio, color, alfa):
    capa = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(capa)
    x, y = xy
    d.ellipse((x - radio, y - radio, x + radio, y + radio), fill=color + (alfa,))
    return capa.filter(ImageFilter.GaussianBlur(radio * 0.45))


def kiosco():
    im = Image.new("RGBA", (W, H), NEGRO + (255,))
    d = ImageDraw.Draw(im)
    # Fondo: degradado, luz cálida y piso
    for y in range(H):
        v = int(24 - 16 * y / H)
        d.line((0, y, W, y), fill=(v + 2, v, v + 1, 255))
    im.alpha_composite(brillo((W, H), (W // 2, 520), 760, (120, 30, 30), 60))
    d.rectangle((0, 1300, W, H), fill=(16, 16, 18, 255))
    d.line((0, 1300, W, 1300), fill=(40, 40, 44, 255), width=2)

    # Letrero superior con el logo
    im.alpha_composite(brillo((W, H), (W // 2, 270), 520, ROJO, 70))
    d = ImageDraw.Draw(im)
    for px in (330, 1374):
        d.rectangle((px, 380, px + 16, 560), fill=(46, 46, 50, 255))
    d.rounded_rectangle((300, 140, 1420, 400), radius=18, fill=NEGRO + (255,), outline=ROJO, width=8)
    d.rounded_rectangle((322, 162, 1398, 378), radius=10, outline=(120, 10, 16), width=2)
    ob = logo("obregom-logo.png", 170)
    im.alpha_composite(ob, (W // 2 - ob.width // 2, 160))
    text_c(d, (W // 2, 352), "PROCESADORA · ALMACENADORA · DISTRIBUIDORA", font("Inter-SemiBold.otf", 26), BLANCO, spacing=4)

    # Vitrina de vidrio: fondo interior, LED y repisas
    gx0, gy0, gx1, gy1 = 200, 560, 1520, 1070
    d.rounded_rectangle((gx0, gy0, gx1, gy1), radius=40, fill=(26, 26, 30, 255))
    im.alpha_composite(brillo((W, H), (W // 2, gy0 + 40), 520, (255, 233, 194), 70))
    d = ImageDraw.Draw(im)
    d.rectangle((gx0 + 40, gy0 + 22, gx1 - 40, gy0 + 32), fill=(255, 240, 210, 255))
    d.rectangle((gx0 + 30, 808, gx1 - 30, 816), fill=(70, 70, 76, 255))
    repisa(im, [empaque(f, b, 210) for f, b in RES], gx0 + 40, gx1 - 40, 806)
    repisa(im, [empaque(f, b, 170) for f, b in CERDO] + [empaque(f, b, 150) for f, b in POLLO], gx0 + 40, gx1 - 40, 1030)
    d = ImageDraw.Draw(im)
    for y, etiqueta in ((816, "RES"), (1032, "CERDO  ·  POLLO")):
        d.rectangle((gx0 + 30, y, gx1 - 30, y + 14), fill=ROJO + (255,))
        tw = d.textlength(etiqueta, font=font("Inter-Bold.otf", 24)) + 40
        d.rounded_rectangle((W // 2 - tw / 2, y - 6, W // 2 + tw / 2, y + 26), radius=6, fill=NEGRO + (255,))
        text_c(d, (W // 2, y + 10), etiqueta, font("Inter-Bold.otf", 24), BLANCO)

    # Vidrio: velo, marco y reflejos
    velo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    v = ImageDraw.Draw(velo)
    v.rounded_rectangle((gx0, gy0, gx1, gy1), radius=40, fill=(255, 255, 255, 14))
    v.polygon([(420, gy0), (520, gy0), (300, gy1), (200, gy1)], fill=(255, 255, 255, 34))
    v.polygon([(1180, gy0), (1220, gy0), (1020, gy1), (980, gy1)], fill=(255, 255, 255, 22))
    im.alpha_composite(velo.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((gx0, gy0, gx1, gy1), radius=40, outline=(58, 58, 64, 255), width=10)

    # Mueble base con marcas
    d.rounded_rectangle((180, 1070, 1540, 1330), radius=22, fill=(15, 15, 18, 255))
    d.rectangle((180, 1070, 1540, 1084), fill=ROJO + (255,))
    ob2 = logo("obregom-logo.png", 150)
    im.alpha_composite(ob2, (500 - ob2.width // 2, 1130))
    dq = panel_drquesos(440, 157)
    im.alpha_composite(dq, (1220 - dq.width // 2, 1126))
    d = ImageDraw.Draw(im)
    text_c(d, (W // 2, 1298), "CERDO · RES · POLLO · EMBUTIDOS · MARISCOS", font("Inter-SemiBold.otf", 24), (170, 170, 176), spacing=3)

    # Sombra y reflejo en el piso
    sombra = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse((160, 1310, 1560, 1380), fill=(0, 0, 0, 200))
    im.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)))
    reflejo = im.crop((180, 1150, 1540, 1330)).transpose(Image.FLIP_TOP_BOTTOM)
    reflejo.putalpha(Image.linear_gradient("L").resize(reflejo.size).point(lambda v: int(v * 0.0 + (255 - v) * 0.18)))
    im.alpha_composite(reflejo, (180, 1340))
    return im.convert("RGB")


if __name__ == "__main__":
    out = AQUI / "salida"
    out.mkdir(exist_ok=True)
    kiosco().save(out / "kiosco-obregom.jpg", quality=92)
    print("ok")
