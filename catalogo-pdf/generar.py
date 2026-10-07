"""Genera catalogo.html (formato Obregón, A4) a partir de los datos del catálogo.

Uso:  python3 catalogo-pdf/generar.py   y luego   node catalogo-pdf/pdf.cjs
"""
from pathlib import Path

AQUI = Path(__file__).parent
IMG = "../assets/img"
WA = "https://wa.me/573164320413?text=Hola%20OBREGOM%2C%20quiero%20hacer%20un%20pedido."
TEL = "316 432 0413"

CERDO = [
    ("hd/cerdo-chuletas", "Chuletas", "", "14.000"),
    ("hd/cerdo-lomo-tajado", "Lomo de cerdo tajado", "", "15.000"),
    ("hd/cerdo-lomo-relajado", "Lomo de cerdo relajado", "", "15.000"),
    ("hd/cerdo-bondiola", "Bondiola de cerdo", "", "15.000"),
    ("hd/cerdo-costilla", "Costilla de cerdo carnuda", "", "13.000"),
    ("hd/cerdo-chicharron", "Chicharrón carnudo", "", "15.000"),
]
RES = [
    ("vacio-hd/res-lomo-fino", "Lomo fino", "", "37.000"),
    ("vacio-hd/res-punta-anca", "Punta de anca", "", "34.000"),
    ("vacio-hd/res-chata", "Chata", "", "28.000"),
    ("vacio-hd/res-muchacho", "Muchacho", "", "28.000"),
    ("vacio-hd/res-tetafulla", "Tetafulla", "", "24.000"),
    ("vacio-hd/res-desmechar", "Carne para desmechar", "", "21.000"),
    ("vacio-hd/res-espaldilla", "Espaldilla", "", "21.000"),
    ("vacio-hd/res-molida", "Molida especial", "", "14.000"),
]
POLLO = [
    ("vacio-hd/pollo-entero", "Pollo entero", "", "9.500"),
    ("vacio-hd/pollo-pechuga-entera", "Pechuga entera", "", "14.000"),
    ("vacio-hd/pollo-filete-pechuga", "Filete de pechuga", "", "17.000"),
    ("vacio-hd/pollo-alas", "Alas de pollo", "", "10.000"),
    ("vacio-hd/pollo-muslo", "Muslo de pollo", "", "9.000"),
    ("vacio-hd/pollo-pierna-pernil", "Pierna pernil", "Muslo + contramuslo", "9.000"),
    ("vacio-hd/pollo-pernil-muslo", "Pernil / muslo", "", "9.000"),
    ("vacio-hd/pollo-alitas-bufalo", "Alitas tipo búfalo", "Naturales", "10.000"),
    ("vacio-hd/pollo-alitas-bbq", "Alitas barbecue", "", "6.000"),
    ("vacio-hd/pollo-corazon", "Corazón de pollo", "", "8.000"),
    ("vacio-hd/pollo-higado", "Hígado de pollo", "", "6.000"),
    ("vacio-hd/pollo-molleja", "Molleja de pollo", "", "8.000"),
    ("vacio-hd/pollo-patas", "Patas de pollo", "", "5.000"),
    ("vacio-hd/pollo-rabadilla", "Rabadilla de pollo", "", "5.000"),
    ("vacio-hd/pollo-pechuga-sin-piel", "Pechuga sin piel", "", "16.000"),
    ("vacio-hd/pollo-pechuga-partida", "Pechuga partida", "", "14.000"),
]
LACTEOS = [
    ("hd/queso-costeno", "Queso costeño", "Bajo en sal", "13.000", "/LB"),
    ("hd/queso-mozzarella", "Queso mozzarella", "", "15.000", "/LB"),
    ("hd/queso-cabra", "Queso de cabra", "", "50.000", "/LB"),
]
CABRA = [("Queso de cabra", "la libra", "50.000"), ("Yogur de cabra", "el litro", "25.000"), ("Leche de cabra", "el litro", "20.000")]
PASABOCAS = [
    ("hd/deditos", "Deditos", "20 unidades", "15.000", "/BANDEJA"),
    ("hd/empanadillas", "Empanadillas", "", "15.000", "/BANDEJA"),
]
EMBUTIDOS = [("Chorizo de pollo y cerdo", "6 unidades · el paquete", "14.000"),
             ("Chorizo de cerdo", "4 unidades · el paquete", "12.000"),
             ("Salchicha Ranch", "12 unidades · el paquete", "15.000")]
PESCADOS = [
    ("hd/pescado-tilapia", "Filete de tilapia", "", "15.000", "/LB"),
    ("hd/pescado-camaron", "Camarón jumbo", "", "28.000", "/LB"),
    ("hd/pescado-salmon", "Filete de salmón", "", "41.000", "/LB"),
]

ICONOS = {
    "medalla": '<svg viewBox="0 0 24 24"><circle cx="12" cy="9" r="6"/><path d="M9.5 9l1.8 1.8L15 7.2"/><path d="M8.5 14l-2 7 3.5-2 2 3 1-7M15.5 14l2 7-3.5-2-2 3"/></svg>',
    "hoja": '<svg viewBox="0 0 24 24"><path d="M5 19c0-8 5-13 15-14-1 10-6 15-14 15M5 19l7-7"/></svg>',
    "frio": '<svg viewBox="0 0 24 24"><path d="M12 2v20M3.3 7l17.4 10M3.3 17L20.7 7M9 3.5l3 2 3-2M9 20.5l3-2 3 2"/></svg>',
    "escudo": '<svg viewBox="0 0 24 24"><path d="M12 2l8 3v6c0 5-3.4 9.3-8 11-4.6-1.7-8-6-8-11V5z"/><path d="M8.5 12l2.5 2.5 4.5-5"/></svg>',
    "camion": '<svg viewBox="0 0 24 24"><path d="M2 6h11v10H2zM13 9h4l4 4v3h-8z"/><circle cx="6" cy="18" r="2"/><circle cx="17" cy="18" r="2"/></svg>',
    "gente": '<svg viewBox="0 0 24 24"><circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6M15 20c0-2 .8-3.8 2-5 2.5 0 4 2 4 5"/></svg>',
    "whatsapp": '<svg viewBox="0 0 32 32" class="solid"><path d="M16 3a13 13 0 0 0-11.2 19.6L3 29l6.6-1.7A13 13 0 1 0 16 3zm0 23.7a10.7 10.7 0 0 1-5.5-1.5l-.4-.2-3.9 1 1-3.8-.2-.4A10.7 10.7 0 1 1 16 26.7zm5.9-8c-.3-.2-1.9-1-2.2-1s-.5-.2-.7.2-.8 1-1 1.2-.4.2-.7 0a8.8 8.8 0 0 1-4.3-3.8c-.3-.6.3-.5 1-1.7.1-.2 0-.4 0-.6l-1-2.4c-.3-.6-.5-.5-.7-.5h-.6a1.2 1.2 0 0 0-.9.4 3.7 3.7 0 0 0-1.1 2.7 6.5 6.5 0 0 0 1.3 3.4 14.7 14.7 0 0 0 5.7 5c2.1.9 2.9 1 4 .8a3.4 3.4 0 0 0 2.2-1.6 2.8 2.8 0 0 0 .2-1.6c0-.2-.3-.3-.6-.5z"/></svg>',
}


def logo(clase=""):
    return (f'<div class="logo {clase}"><span class="logo__word">OBREGO<span>M</span></span>'
            f'<span class="logo__sub">Distribuidora</span></div>')


def pie(n):
    return f'''<footer class="pie">
      {logo("logo--pie")}
      <p class="pie__lema">Calidad <b>|</b> Frescura <b>|</b> Buen precio<span>Tu mejor opción</span></p>
      <p class="pie__tel">Pedidos y domicilios<strong>{TEL}</strong></p>
      <span class="pie__num">{n:02d}</span>
    </footer>'''


def franja():
    items = [("medalla", "Productos <em>frescos</em>", "de excelente calidad"),
             ("hoja", "Calidad en", "cada producto"),
             ("frio", "Empacados <em>al vacío</em>", "por libra (lb)"),
             ("escudo", "Frescura", "siempre")]
    celdas = "".join(f'<div class="franja__item">{ICONOS[i]}<p><b>{a}</b>{b}</p></div>' for i, a, b in items)
    return f'<div class="franja">{celdas}</div>'


def tarjeta(img, nombre, sub, precio, unidad="/LB"):
    s = f"<small>{sub}</small>" if sub else ""
    return (f'<article class="pack"><div class="pack__img"><img src="{IMG}/{img}.jpg" alt=""></div>'
            f'<h3 class="pack__name">{nombre}{s}</h3>'
            f'<p class="pack__price">${precio} <small>{unidad}</small></p></article>')


def pagina_guia(n, clave, alt):
    return f'''
  <section class="page page--guia">
    <div class="guia"><img src="{IMG}/piezas/{clave}-guia.jpg" alt="{alt}"></div>
    {pie(n)}
  </section>'''


def pagina_vacio(n, palabra, items, cols, extra=""):
    tarjetas = "\n        ".join(tarjeta(*i) for i in items)
    return f'''
  <section class="page page--vacio">
    <div class="cuerpo">
      <header class="vhead">
        <div class="vhead__title">
          <span class="pill">Lista de precios</span>
          <h2>{palabra}</h2>
          <span class="pill">Todos sus cortes</span>
        </div>
        <p class="vhead__note">Todos los productos son empacados <b>al vacío</b><span>Precio por libra (lb)</span></p>
      </header>
      <p class="vtag">Calidad en cada producto <b>•</b> Frescura siempre</p>
      <div class="packs packs--{cols} {palabra.lower()}">
        {tarjetas}
      </div>
      {extra}
      {franja()}
    </div>
    {pie(n)}
  </section>'''


def titulo(texto):
    return f'<h2 class="titulo"><span>{texto}</span></h2>'


def lista(titulo_lista, filas, nota=""):
    li = "".join(f'<li><span>{a}<small>{b}</small></span><b>${c}</b></li>' for a, b, c in filas)
    n = f'<p class="lista__nota">{nota}</p>' if nota else ""
    return f'<article class="lista"><h3>{titulo_lista}</h3><ul>{li}</ul>{n}</article>'


categorias = [
    ("hd/cerdo-chuletas", "Cerdo", "03"), ("vacio-hd/res-lomo-fino", "Res", "05"),
    ("vacio-hd/pollo-filete-pechuga", "Pollo", "07"), ("hd/queso-costeno", "Lácteos", "09"),
    ("hd/empanadillas", "Pasabocas", "09"), ("hd/pescado-salmon", "Pescados", "10"),
]
cats = "".join(f'<div class="cat"><img src="{IMG}/{i}.jpg" alt=""><p>{t}<span>pág. {p}</span></p></div>'
               for i, t, p in categorias)

portada = f'''
  <section class="page page--portada">
    <span class="diag diag--a"></span><span class="diag diag--b"></span>
    <span class="diag diag--c"></span><span class="diag diag--d"></span>
    <div class="portada">
      <div class="portada__top">
        {logo("logo--grande")}
        <img class="badge" src="{IMG}/drquesos.png" alt="DrQuesos">
      </div>
      <p class="portada__kicker">Catálogo de</p>
      <h1>Productos</h1>
      <p class="portada__sub">Calidad en cada entrega</p>
      <div class="cats">{cats}</div>
      <div class="ventajas">
        <div>{ICONOS["medalla"]}<p>Productos de excelente calidad</p></div>
        <div>{ICONOS["camion"]}<p>Entregas a tiempo</p></div>
        <div>{ICONOS["frio"]}<p>Empacados al vacío</p></div>
        <div>{ICONOS["gente"]}<p>Atención personalizada</p></div>
      </div>
      <a class="portada__wa" href="{WA}">{ICONOS["whatsapp"]}<span>Pedidos y domicilios<strong>{TEL}</strong></span></a>
      <p class="portada__lema">Tu aliado en distribución de alimentos</p>
    </div>
  </section>'''

otros = f'''
  <section class="page page--otros">
    <div class="cuerpo">
      <header class="vhead">
        <div class="vhead__title">
          <span class="pill">Lista de precios</span>
          <h2>Más productos</h2>
          <span class="pill">Lácteos · Pasabocas · Embutidos</span>
        </div>
        <p class="vhead__note">Productos frescos y de <b>calidad</b><span>Precios al cliente final</span></p>
      </header>
      <div class="grupo">
      {titulo("Lácteos y productos de cabra")}
      <div class="packs packs--4 packs--bajo">
        {"".join(tarjeta(*i) for i in LACTEOS)}
        {lista("Productos de cabra", CABRA, "Disponibilidad sujeta a inventario")}
      </div>
      {titulo("Pasabocas y embutidos")}
      <div class="packs packs--4 packs--bajo">
        {"".join(tarjeta(*i) for i in PASABOCAS)}
        <div class="span2">{lista("Embutidos", EMBUTIDOS)}</div>
      </div>
      </div>
      {franja()}
    </div>
    {pie(9)}
  </section>'''

pasos = [("Escoge tus productos", "Revisa este catálogo y elige los cortes y cantidades por libra."),
         ("Escríbenos por WhatsApp", f"Envía tu pedido al {TEL}. Te confirmamos disponibilidad y valor."),
         ("Recibe tu domicilio", "Entregamos a tiempo, con tus productos frescos y empacados al vacío.")]
pasos_html = "".join(f'<li><span class="paso__n">{i}</span><div><b>{a}</b><p>{b}</p></div></li>'
                     for i, (a, b) in enumerate(pasos, 1))

final = f'''
  <section class="page page--final">
    <div class="cuerpo">
      {titulo("Pescados y mariscos")}
      <div class="packs packs--3">
        {"".join(tarjeta(*i) for i in PESCADOS)}
      </div>
      <div class="pedido">
        <h2>¿Cómo hacer tu pedido?</h2>
        <ol class="pasos">{pasos_html}</ol>
        <a class="pedido__wa" href="{WA}">{ICONOS["whatsapp"]}<span>Pedidos y domicilios<strong>{TEL}</strong></span></a>
        <p class="pedido__nota">Precios al cliente final, sujetos a cambio y a disponibilidad de inventario.
          Presentación por libra salvo indicación diferente. Productos disponibles según zona.</p>
      </div>
    </div>
    {pie(10)}
  </section>'''

paginas = (portada
           + pagina_guia(2, "cerdo", "Guía visual de cortes de cerdo")
           + pagina_vacio(3, "Cerdo", CERDO, 3)
           + pagina_guia(4, "res", "Guía visual de cortes de res")
           + pagina_vacio(5, "Res", RES, 4)
           + pagina_guia(6, "pollo", "Guía visual de cortes de pollo")
           + pagina_vacio(7, "Pollo", POLLO, 4)
           + otros.replace(pie(9), pie(8))
           + final.replace(pie(10), pie(9)))

# Las páginas reales quedan: 1 portada, 2-3 cerdo, 4-5 res, 6-7 pollo, 8 otros, 9 pescados y pedido
paginas = paginas.replace("pág. 03", "pág. 02").replace("pág. 05", "pág. 04").replace("pág. 07", "pág. 06") \
                 .replace("pág. 09", "pág. 08").replace("pág. 10", "pág. 09")

html = f'''<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Catálogo OBREGOM Distribuidora</title>
<link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=Oswald:wght@500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="catalogo.css">
</head>
<body>
{paginas}
</body>
</html>
'''
(AQUI / "catalogo.html").write_text(html, encoding="utf-8")
print("catalogo.html listo")
