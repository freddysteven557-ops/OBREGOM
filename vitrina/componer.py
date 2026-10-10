"""Limpia la foto de la vitrina y le aplica el branding ObreGom + DrQuesos.

Uso: python3 vitrina/componer.py  ->  vitrina/salida/vitrina-obregom-drquesos.jpg
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from vinilo import CREMA_Q, ROJO, font, logo, vinilo

AQUI = Path(__file__).parent
ORIGINAL = AQUI / "original" / "vitrina-original.jpg"
SALIDA = AQUI / "salida"

# Geometría del panel negro frontal (coordenadas en la foto de 4000x3000)
X0, X1 = 335, 4000
TOP = [(335, 2297), (1000, 2301), (2000, 2305), (3300, 2310), (4000, 2314)]
BOT = [(335, 2612), (700, 2640), (1000, 2660), (1600, 2680), (2000, 2695), (2800, 2715), (4000, 2735)]
# Esquina redondeada inferior izquierda del mueble (lo que queda fuera es la rejilla de la vitrina vecina)
PANEL = [(335, 2290), (4000, 2306), (4000, 2742), (2000, 2700), (1000, 2665), (700, 2645),
         (460, 2612), (345, 2462)]
# Panel de la vitrina vecina (izquierda)
QUESO_ZONA = [(2310, 850), (2780, 830), (2960, 765), (3190, 770), (3260, 1110), (2400, 1110), (2320, 960)]
VECINA = [(0, 2232), (302, 2258), (338, 2452), (350, 2476), (0, 2482)]


def interp(pts, xs):
    px, py = zip(*pts)
    return np.interp(xs, px, py)


def corregir_color(img):
    """Quita el tinte magenta de la luz LED dentro de la vitrina y el amarillo del exterior."""
    a = np.asarray(img).astype(np.float32)
    # Componente magenta: cuánto superan R y B al verde. Los rojos de la carne (B≈G) casi no se tocan.
    mag = np.clip(np.minimum(a[..., 0], a[..., 2]) - a[..., 1], 0, None)
    k = 0.55   # con k≈0.59 el magenta queda neutro; un poco menos evita virar a verde
    a[..., 0] -= k * mag
    a[..., 2] -= k * mag
    a[..., 1] += 0.70 * k * mag          # conserva la luminancia
    a *= np.array([0.98, 1.0, 1.06], np.float32)   # quita lo amarillento del piso/pared
    # Casi-blancos (queso, grasa, brillos) quemados por el LED: llevarlos a blanco crema
    lo = a.min(-1, keepdims=True)
    w = np.clip((lo - 150) / 60, 0, 1) * 0.85
    y = a @ np.array([0.299, 0.587, 0.114], np.float32)
    a = y[..., None] + (a - y[..., None]) * (1 - w) + w * np.array([4, 2, -6], np.float32)
    # Zona del queso: el LED lo tiñe de rosado; se lleva a blanco crema
    zq = Image.new("L", img.size, 0)
    ImageDraw.Draw(zq).polygon(QUESO_ZONA, fill=255)
    zq = np.asarray(zq.filter(ImageFilter.GaussianBlur(25))).astype(np.float32)[..., None] / 255
    zq = zq * np.clip((a.min(-1, keepdims=True) - 90) / 60, 0, 1)
    y = a @ np.array([0.299, 0.587, 0.114], np.float32)
    crema = y[..., None] * np.array([1.10, 1.07, 0.97], np.float32)
    a = a * (1 - zq) + crema * zq
    # Curva suave de contraste + leve saturación
    a = np.clip(a, 0, 255) / 255
    a = a + 0.10 * (a - a ** 2) * (2 * a - 1) * -1   # S-curve ligera
    lum = a.mean(-1, keepdims=True)
    a = lum + (a - lum) * 1.06
    out = Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8))
    return out.filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))


# Etiquetas DrQuesos sobre los bloques al vacío: (centro x, centro y, ancho, giro°)
ETIQUETAS = [(2490, 1015, 140, -2), (2720, 1020, 135, 1), (2905, 995, 140, -3), (3140, 1015, 145, 2),
             (2450, 905, 115, -1), (2720, 890, 120, 2), (3090, 835, 110, -4)]


def etiqueta_queso(w):
    """Etiqueta pequeña tipo sticker para cada bloque de queso (renderizada a 4x)."""
    s = 4
    W, H = w * s, int(w * 0.42) * s
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, W - 1, H - 1), radius=H // 4, fill=ROJO)
    d.rounded_rectangle((3 * s, 3 * s, W - 1 - 3 * s, H - 1 - 3 * s), radius=H // 5, fill=CREMA_Q)
    marca = logo("drquesos-logo.png", int(H * 0.72))
    im.alpha_composite(marca, ((W - marca.width) // 2, (H - marca.height) // 2))
    return im.resize((w, H // s), Image.LANCZOS)


def pegar_etiquetas(foto):
    for cx, cy, w, ang in ETIQUETAS:
        e = etiqueta_queso(w).rotate(ang, resample=Image.BICUBIC, expand=True)
        e = e.filter(ImageFilter.GaussianBlur(0.6))
        r, g, b, a = e.split()
        r, g, b = (c.point(lambda v: int(v * 0.9)) for c in (r, g, b))   # misma luz que el queso
        e = Image.merge("RGBA", (r, g, b, a.point(lambda v: int(v * 0.9))))  # se ve a través del plástico
        foto.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
    return foto


def warp_panel(art, foto):
    """Pega el arte en el panel siguiendo el borde superior/inferior y la perspectiva."""
    H, W = foto.shape[:2]
    xs = np.arange(X0, X1)
    top, bot = interp(TOP, xs), interp(BOT, xs)
    h = bot - top
    # Perspectiva horizontal: la escala local es proporcional a la altura local
    du = 1 / h
    u = np.concatenate([[0], np.cumsum(du)[:-1]])
    u = u / (u[-1] + du[-1]) * (art.shape[1] - 1)

    y0, y1 = int(top.min()) - 2, int(bot.max()) + 2
    ys = np.arange(y0, y1)[:, None]
    v = (ys - top[None, :]) / h[None, :] * (art.shape[0] - 1)
    U = np.broadcast_to(u[None, :], v.shape)
    res = bilinear(art, U, v)
    inside = ((v >= 0) & (v <= art.shape[0] - 1)).astype(np.float32)
    return res, inside, (X0, y0)


def bilinear(img, x, y):
    h, w = img.shape[:2]
    x = np.clip(x, 0, w - 1.001)
    y = np.clip(y, 0, h - 1.001)
    x0, y0 = np.floor(x).astype(int), np.floor(y).astype(int)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    a = img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx
    b = img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def brillo_vinilo(rgb, rng):
    """Simula vinilo impreso bajo la luz del local: sin blancos puros, brillo especular y grano."""
    h, w = rgb.shape[:2]
    rgb = rgb * 0.86 + 6
    yy = np.linspace(0, 1, h)[:, None, None]
    xx = np.linspace(0, 1, w)[None, :, None]
    sombra_labio = 1 - 0.35 * np.exp(-yy / 0.06)                    # sombra bajo el riel superior
    caida = 1 - 0.18 * yy                                          # se oscurece hacia abajo
    rgb = rgb * sombra_labio * caida
    # Reflejos de las lámparas sobre el plástico brillante
    g = (np.exp(-((xx - 0.33) / 0.10) ** 2 - ((yy - 0.22) / 0.16) ** 2) * 0.9
         + np.exp(-((xx - 0.72) / 0.07) ** 2 - ((yy - 0.25) / 0.14) ** 2) * 0.55
         + np.exp(-((yy - 0.05) / 0.035) ** 2) * 0.5)
    spec = np.array([200, 190, 205], np.float32) * g * 0.22
    rgb = 255 - (255 - rgb) * (1 - spec / 255)                     # screen
    rgb = rgb + rng.normal(0, 2.2, rgb.shape)
    return rgb


def componer():
    rng = np.random.default_rng(7)
    foto = corregir_color(Image.open(ORIGINAL).convert("RGB"))
    W, H = foto.size
    base = np.asarray(foto).astype(np.float32)

    art = np.asarray(vinilo().convert("RGB")).astype(np.float32)
    art = np.asarray(Image.fromarray(art.astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6))).astype(np.float32)

    # Panel principal
    res, inside, (ox, oy) = warp_panel(art, base)
    res = brillo_vinilo(res, rng)
    mask = Image.new("L", (W, H), 0)
    ImageDraw.Draw(mask).polygon(PANEL, fill=255)
    mask = np.asarray(mask.filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32) / 255
    hh, ww = res.shape[:2]
    m = mask[oy:oy + hh, ox:ox + ww][..., None] * inside[..., None]
    base[oy:oy + hh, ox:ox + ww] = base[oy:oy + hh, ox:ox + ww] * (1 - m) + res * m

    # Vitrina vecina: se ve el extremo derecho del mismo vinilo
    trozo = Image.fromarray(art[:, 6150:].astype(np.uint8))
    vx0, vy0, vx1, vy1 = 0, 2226, 352, 2486
    trozo = trozo.resize((vx1 - vx0, vy1 - vy0), Image.LANCZOS)
    t = brillo_vinilo(np.asarray(trozo).astype(np.float32) * 0.82, rng)
    vm = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vm).polygon(VECINA, fill=255)
    vm = np.asarray(vm.filter(ImageFilter.GaussianBlur(1.5))).astype(np.float32)[vy0:vy1, vx0:vx1, None] / 255
    base[vy0:vy1, vx0:vx1] = base[vy0:vy1, vx0:vx1] * (1 - vm) + t * vm

    out = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).convert("RGBA")
    return pegar_etiquetas(out).convert("RGB")


if __name__ == "__main__":
    SALIDA.mkdir(exist_ok=True)
    img = componer()
    img.save(SALIDA / "vitrina-obregom-drquesos.jpg", quality=92)
    # Antes / después
    antes = Image.open(ORIGINAL).convert("RGB").resize((1600, 1200), Image.LANCZOS)
    despues = img.resize((1600, 1200), Image.LANCZOS)
    comp = Image.new("RGB", (3220, 1290), (20, 18, 20))
    comp.paste(antes, (0, 90))
    comp.paste(despues, (1620, 90))
    d = ImageDraw.Draw(comp)
    f = font("BebasNeue-Regular.ttf", 64)
    d.text((800, 45), "ANTES", font=f, fill=(235, 235, 235), anchor="mm")
    d.text((2420, 45), "DESPUÉS · OBREGOM + DRQUESOS", font=f, fill=ROJO, anchor="mm")
    comp.save(SALIDA / "antes-despues.jpg", quality=88)
    print("ok", img.size)
