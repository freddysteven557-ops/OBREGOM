"""Arte plano del vinilo frontal con los logos reales de ObreGom y DrQuesos."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

AQUI = Path(__file__).parent
FONTS = AQUI / "fonts"
MARCA = AQUI / "marca"
INTER = Path("/usr/share/fonts/opentype/inter")

# Paleta ObreGom
NEGRO = (11, 11, 13)
ROJO = (225, 14, 23)
BLANCO = (245, 245, 245)
GRIS = (170, 170, 176)
CREMA_Q = (243, 226, 186)


def font(name, size):
    if name.startswith("Inter"):
        return ImageFont.truetype(str(INTER / name), size)
    return ImageFont.truetype(str(FONTS / name), size)


def text_c(d, xy, s, f, fill, spacing=0):
    """Texto centrado; `spacing` agrega espacio entre letras (px)."""
    if not spacing:
        d.text(xy, s, font=f, fill=fill, anchor="mm")
        return
    widths = [d.textlength(ch, font=f) for ch in s]
    x = xy[0] - (sum(widths) + spacing * (len(s) - 1)) / 2
    for ch, w in zip(s, widths):
        d.text((x, xy[1]), ch, font=f, fill=fill, anchor="lm")
        x += w + spacing


def logo(nombre, alto):
    im = Image.open(MARCA / nombre).convert("RGBA")
    return im.resize((round(im.width * alto / im.height), alto), Image.LANCZOS)


def esquinas(d, x0, y0, x1, y1, largo, grosor, color):
    """Esquinas rojas en L, como en la imagen de marca."""
    for x, y, sx, sy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        d.rectangle((min(x, x + sx * largo), min(y, y + sy * grosor),
                     max(x, x + sx * largo), max(y, y + sy * grosor)), fill=color)
        d.rectangle((min(x, x + sx * grosor), min(y, y + sy * largo),
                     max(x, x + sx * grosor), max(y, y + sy * largo)), fill=color)


def panel_drquesos(W, H):
    """Panel crema con textura de queso y el logo DrQuesos quemado."""
    src = Image.open(MARCA / "drquesos-banner.jpg").convert("RGB").crop((330, 20, 1200, 330))
    src = src.resize((W, H), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, W - 1, H - 1), radius=48, fill=255)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(src, (0, 0), mask)
    ImageDraw.Draw(out).rounded_rectangle((0, 0, W - 1, H - 1), radius=48, outline=ROJO, width=14)
    return out


def vinilo(W=7360, H=800):
    """Banda completa del frente. Escala 2:1 respecto al panel en la foto (x 335–4000)."""
    im = Image.new("RGBA", (W, H), NEGRO + (255,))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 22, W, 30), fill=ROJO)
    d.rectangle((0, H - 30, W, H - 22), fill=ROJO)

    # ObreGom (izquierda) y DrQuesos (derecha)
    ob = logo("obregom-logo.png", 600)
    im.alpha_composite(ob, (1700 - ob.width // 2, 400 - ob.height // 2))
    dq = panel_drquesos(1640, 584)
    sombra = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sombra.paste((0, 0, 0, 200), (5700 - dq.width // 2 + 12, 400 - dq.height // 2 + 16,
                                  5700 + dq.width // 2 + 12, 400 + dq.height // 2 + 16))
    im.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)))
    im.alpha_composite(dq, (5700 - dq.width // 2, 400 - dq.height // 2))

    # Centro: lo que hace la empresa y las líneas de producto
    cx = 3720
    d.ellipse((cx - 16, 214, cx + 16, 246), fill=ROJO)
    d.line((cx - 620, 230, cx - 60, 230), fill=ROJO, width=5)
    d.line((cx + 60, 230, cx + 620, 230), fill=ROJO, width=5)
    text_c(d, (cx, 360), "PROCESADORA · ALMACENADORA · DISTRIBUIDORA", font("Inter-SemiBold.otf", 64), BLANCO, spacing=10)
    text_c(d, (cx, 490), "CERDO · RES · POLLO · EMBUTIDOS · MARISCOS", font("Inter-ExtraBold.otf", 70), ROJO, spacing=6)
    text_c(d, (cx, 600), "Empacados al vacío", font("Inter-Medium.otf", 58), GRIS)

    # Extremos: esquinas rojas
    for x0, x1 in ((140, 620), (W - 620, W - 140)):
        esquinas(d, x0, 150, x1, H - 150, 120, 10, ROJO)
    return im


if __name__ == "__main__":
    out = AQUI / "salida"
    out.mkdir(exist_ok=True)
    v = vinilo()
    v.convert("RGB").save(out / "vinilo-frontal.png")
    print("ok", v.size)
