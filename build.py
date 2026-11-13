#!/usr/bin/env python3
"""Genera el catálogo estático en _site/.

Todo lo que cambia de un cliente a otro está en config.json (nombre, colores, logo,
WhatsApp, planilla, textos, módulos). Este archivo no se toca para un cliente nuevo.

Fuente de productos (en orden de prioridad):
  1. La variable de entorno SHEET_CSV_URL (si se quiere pisar la de config.json).
  2. "planilla_csv" de config.json (Google Sheets publicada como CSV).
  3. El archivo local data/productos.csv.

Otras variables de entorno (las pone la GitHub Action):
  SOLO_SI_CAMBIA=true  no publica si los productos son iguales a los de la página actual.
  FORZAR=true          publica aunque haya muchos menos productos que antes.
  QUIENES_SOMOS        pisa "quienes_somos_modo" de config.json: "modal", "pagina" u "oculto" (sin botón, cartel ni página).

Solo usa la biblioteca estándar de Python: no hace falta instalar nada.
"""
import csv
import html
import io
import json
import os
import shutil
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

RAIZ = Path(__file__).parent
SALIDA = RAIZ / "_site"

# Nombres de columna aceptados (sin importar mayúsculas ni tildes).
COLUMNAS = {
    "categoria": "categoria",
    "nombre": "nombre",
    "descripcion": "descripcion",
    "presentacion": "presentacion",
    "precio": "precio",
    "disponible": "disponible",
    "foto": "foto",
}
# Sin estas columnas la página saldría rota (sin productos o todo en "Consultar").
OBLIGATORIAS = ("nombre", "precio")
# Si quedan menos de esta fracción de los productos publicados, se frena (filas borradas por error).
MINIMO_RESPECTO_ANTERIOR = 0.5
# Formas de mostrar «¿Quiénes somos?»; la primera es la que se usa si la variable no está o está mal escrita.
MODOS_QUIENES = ("modal", "pagina", "oculto")
PAGINA_QUIENES = "quienes-somos.html"
PAGINA_PEDIDOS = "pedidos-especiales.html"
PAGINA_CATALOGO = "./"  # el catálogo es la página de entrada (index.html)
NOMBRE_CATERING = "Catering"  # lo que ve el usuario; la clave de config.json sigue siendo "pedidos_especiales"
# Claves de config.json sin las que no se puede armar la página.
CONFIG_OBLIGATORIAS = ("nombre", "whatsapp")
# Colores de config.json -> variables CSS que usan las plantillas.
COLORES = {
    "principal": ("--principal", "#1d5e24"),
    "principal_oscuro": ("--principal-osc", "#154519"),
    "secundario": ("--secundario", "#89b335"),
    "secundario_oscuro": ("--secundario-osc", "#6f8f28"),
    "sobre_principal": ("--sobre-principal", "#ffffff"),
    "sobre_secundario": ("--sobre-secundario", "#ffffff"),
    "acento": ("--acento", None),  # sin valor en config.json, toma el de "secundario"
    "fondo": ("--fondo", "#f3f6ee"),
    "tarjetas": ("--papel", "#ffffff"),
    "texto": ("--tinta", "#1f2a1e"),
    "texto_suave": ("--suave", "#5e6b5a"),
    "bordes": ("--linea", "#dde5d2"),
    "alerta": ("--alerta", "#d9485f"),
}


def normalizar(texto):
    reemplazos = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return texto.strip().translate(reemplazos).lower()


def leer_config():
    config = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
    faltan = [c for c in CONFIG_OBLIGATORIAS if not str(config.get(c, "")).strip()]
    if faltan:
        sys.exit(f"ERROR: en config.json faltan {', '.join(faltan)}. No se publica nada.")
    config["whatsapp"] = "".join(ch for ch in str(config["whatsapp"]) if ch.isdigit())
    if config["whatsapp"].startswith("54911000000"):
        print("::warning::El WhatsApp de config.json es el de ejemplo: cambialo por el del cliente.")
    return config


def leer_csv(config):
    url = (os.environ.get("SHEET_CSV_URL", "") or config.get("planilla_csv", "")).strip()
    if url:
        print(f"Descargando planilla desde {url[:60]}...")
        with urllib.request.urlopen(url, timeout=30) as r:
            texto = r.read().decode("utf-8-sig")
    else:
        print("Usando data/productos.csv")
        texto = (RAIZ / "data" / "productos.csv").read_text(encoding="utf-8-sig")
    lector = csv.DictReader(io.StringIO(texto))
    encontradas = [c for c in (lector.fieldnames or []) if c]
    faltan = [c for c in OBLIGATORIAS if c not in {COLUMNAS.get(normalizar(x)) for x in encontradas}]
    if faltan:
        sys.exit(
            f"ERROR: a la planilla le faltan las columnas {', '.join(faltan)}. "
            f"Columnas encontradas: {', '.join(encontradas) or '(ninguna)'}. "
            "Revisá que nadie haya renombrado o borrado la primera fila. No se publica nada."
        )
    return list(lector)


def leer_catering(config):
    """Opciones y extras del cotizador. Salen del link "catering_csv" (Google Sheets publicada como CSV).
    Si el link está vacío, no responde o la hoja no trae opciones, se usa data/catering.csv como respaldo.
    Columnas: Tipo (Opción o Extra), Nombre, Descripción (se acepta «Descipción»), Precio y Cobro
    (por persona o fijo; las opciones siempre se cobran por persona)."""
    url = config.get("pedidos_especiales", {}).get("catering_csv", "").strip()
    local = RAIZ / "data" / "catering.csv"
    if url:
        print(f"Descargando cotizador desde {url[:60]}...")
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                texto = r.read().decode("utf-8-sig")
            datos = parsear_catering(texto)
            if datos["opciones"]:
                return datos
            print("::warning::La hoja del cotizador no tiene opciones. Se usa data/catering.csv.")
        except Exception as e:
            print(f"::warning::No se pudo leer la hoja del cotizador ({e}). Se usa data/catering.csv.")
    else:
        print("Usando data/catering.csv")
    datos = parsear_catering(local.read_text(encoding="utf-8-sig"))
    if not datos["opciones"]:
        print("::warning::El cotizador no tiene ninguna fila de tipo Opción.")
    return datos


def parsear_catering(texto):
    opciones, extras = [], []
    for fila in csv.DictReader(io.StringIO(texto)):
        campos = {normalizar(k): (v or "").strip() for k, v in fila.items() if k}
        nombre = campos.get("nombre", "")
        if not nombre:
            continue
        tipo = normalizar(campos.get("tipo", ""))
        if tipo not in ("opcion", "extra"):
            print(f"::warning::Cotizador: «{nombre}» tiene Tipo «{campos.get('tipo', '')}»; tiene que ser Opción o Extra. Se ignora.")
            continue
        persona = tipo == "opcion" or normalizar(campos.get("cobro", "")).endswith("persona")
        (opciones if tipo == "opcion" else extras).append({
            "nombre": nombre,
            "detalle": campos.get("descripcion") or campos.get("descipcion", ""),
            "precio": parsear_precio(campos.get("precio", "")) or 0,
            "cobro": "persona" if persona else "fijo",
        })
    return {"opciones": opciones, "extras": extras}


def parsear_precio(valor):
    limpio = (valor or "").replace("$", "").replace(".", "").replace(",", ".").strip()
    try:
        return round(float(limpio))
    except ValueError:
        return None


def revisar_fotos(productos):
    """Si una foto no está en img/, avisa en el log y la deja vacía: la página muestra el emoji."""
    disponibles = {f.name for f in (RAIZ / "img").iterdir()} if (RAIZ / "img").is_dir() else set()
    por_minuscula = {nombre.lower(): nombre for nombre in disponibles}
    for p in productos:
        foto = p.get("foto", "")
        if not foto or foto.startswith(("http://", "https://")) or foto in disponibles:
            continue
        real = por_minuscula.get(foto.lower())
        if real:
            # Los servidores distinguen mayúsculas: "Acelga.JPG" no encuentra "acelga.jpg".
            print(f"::warning::Foto de «{p['nombre']}»: se usa «{real}» en vez de «{foto}».")
            p["foto"] = real
        else:
            print(f"::warning::Falta la foto «{foto}» de «{p['nombre']}» en img/. Se muestra el emoji hasta que la subas.")
            p["foto"] = ""


def ordenar_categorias(productos, config):
    """Categorías en el orden de la planilla, salvo las de "categorias_primero", que van adelante si tienen productos."""
    primeras = [normalizar(c) for c in config.get("categorias_primero", [])]
    categorias = list(dict.fromkeys(p["categoria"] for p in productos))
    return sorted(
        categorias,
        key=lambda c: primeras.index(normalizar(c)) if normalizar(c) in primeras else len(primeras),
    )


def limpiar_filas(filas):
    productos = []
    for fila in filas:
        p = {}
        for clave, valor in fila.items():
            if clave is None:
                continue
            k = COLUMNAS.get(normalizar(clave))
            if k:
                p[k] = (valor or "").strip()
        if not p.get("nombre"):
            continue  # filas vacías o de notas
        p["categoria"] = p.get("categoria") or "Otros"
        p["precio"] = parsear_precio(p.get("precio"))
        p["disponible"] = normalizar(p.get("disponible", "si")) not in ("no", "0", "false", "sin stock", "agotado")
        productos.append(p)
    return productos


WA_SVG = '<path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.2-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.1-.3-.2-.5-.3Z"/>'
IG_SVG = '<path d="M7.5 2h9A5.5 5.5 0 0 1 22 7.5v9a5.5 5.5 0 0 1-5.5 5.5h-9A5.5 5.5 0 0 1 2 16.5v-9A5.5 5.5 0 0 1 7.5 2Zm0 2A3.5 3.5 0 0 0 4 7.5v9A3.5 3.5 0 0 0 7.5 20h9a3.5 3.5 0 0 0 3.5-3.5v-9A3.5 3.5 0 0 0 16.5 4h-9ZM12 7a5 5 0 1 1 0 10 5 5 0 0 1 0-10Zm0 2a3 3 0 1 0 0 6 3 3 0 0 0 0-6Zm5.25-3.5a1.25 1.25 0 1 1 0 2.5 1.25 1.25 0 0 1 0-2.5Z"/>'
# Ícono "users" de Lucide (lucide.dev, licencia ISC): va con trazo, no con relleno como los de redes.
QUIENES_SVG = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>'
    '<path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>'
)
# Ícono "message-square-text" de Lucide: catering.
PEDIDOS_SVG = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>'
    '<path d="M13 8H7"/><path d="M17 12H7"/></svg>'
)


def sellos(config):
    """Sellos a la izquierda del logo (por ejemplo "Sin TACC"). Cada uno con imagen o emoji; vacío si no hay."""
    items = []
    for s in config.get("sellos", []):
        if s.get("imagen"):
            icono = f'<img src="{html.escape(s["imagen"])}" alt="" width="34" height="34">'
        else:
            icono = f'<span class="copo" aria-hidden="true">{html.escape(s.get("emoji", "✔️"))}</span>'
        titulo = f' title="{html.escape(s["detalle"])}"' if s.get("detalle") else ""
        items.append(f"<li{titulo}>{icono}{html.escape(s['texto'])}</li>")
    return f'<ul class="sellos" aria-label="Características">{"".join(items)}</ul>' if items else ""


def mezclar(color_a, color_b, parte_a):
    """Mezcla dos colores #rrggbb: `parte_a` (0 a 1) de color_a y el resto de color_b."""
    a, b = (tuple(int(c.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)) for c in (color_a, color_b))
    return "#" + "".join(f"{round(x * parte_a + y * (1 - parte_a)):02x}" for x, y in zip(a, b))


def estilos_marca(config):
    """Variables CSS con los colores y las fuentes de config.json."""
    colores = config.get("colores", {})
    fuentes = config.get("fuentes", {})
    secundario = colores.get("secundario", COLORES["secundario"][1])
    lineas = [f"    {var}: {colores.get(clave, defecto or secundario)};" for clave, (var, defecto) in COLORES.items()]
    # Borde de campos y chips: "bordes" es muy suave para marcar un control (WCAG pide 3:1), así que sale de
    # mezclar el texto con las tarjetas, salvo que config.json defina "bordes_controles".
    texto = colores.get("texto", COLORES["texto"][1])
    tarjetas = colores.get("tarjetas", COLORES["tarjetas"][1])
    try:
        borde_control = colores.get("bordes_controles") or mezclar(texto, tarjetas, .55)
    except ValueError:
        borde_control = "#767676"  # colores que no son #rrggbb: gris que cumple 3:1 sobre blanco
    lineas.append(f"    --borde-control: {borde_control};")
    lineas.append(f'    --fuente-titulos: "{fuentes.get("titulos", "Fraunces")}";')
    lineas.append(f'    --fuente-texto: "{fuentes.get("texto", "Nunito Sans")}";')
    return "  :root {\n" + "\n".join(lineas) + "\n  }\n"


FUENTE_MANUSCRITA = "Caveat"  # la comanda del cotizador, escrita a mano


def link_fuentes(config, manuscrita=False):
    """Link a Google Fonts con las dos fuentes de config.json (y la manuscrita de la comanda si se pide)."""
    fuentes = config.get("fuentes", {})
    familias = dict.fromkeys([fuentes.get("titulos", "Fraunces"), fuentes.get("texto", "Nunito Sans")])
    query = "&".join(f"family={f.replace(' ', '+')}:wght@400;600;800" for f in familias)
    if manuscrita:
        query += f"&family={FUENTE_MANUSCRITA}:wght@500;700"
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        f'<link href="https://fonts.googleapis.com/css2?{query}&display=swap" rel="stylesheet">'
    )


def pedidos_activo(config):
    return bool(config.get("pedidos_especiales", {}).get("activo"))


def modo_quienes(config):
    """'modal', 'pagina', o None si config.json no tiene el texto o el modo es 'oculto' (no aparece el botón)."""
    if not config.get("quienes_somos"):
        return None
    pedido = os.environ.get("QUIENES_SOMOS", "") or config.get("quienes_somos_modo", "")
    modo = normalizar(pedido) or MODOS_QUIENES[0]
    if modo not in MODOS_QUIENES:
        print(f"::warning::QUIENES_SOMOS={pedido!r} no es válido (usá {' o '.join(MODOS_QUIENES)}). Se usa {MODOS_QUIENES[0]}.")
        modo = MODOS_QUIENES[0]
    return None if modo == "oculto" else modo


def texto_quienes(config):
    return "".join(f"<p>{html.escape(parrafo)}</p>" for parrafo in config.get("quienes_somos", []))


def modal_quienes(config):
    return (
        '<dialog class="modal" id="quienes" aria-labelledby="quienes-titulo"><div class="contenido">'
        '<button class="cerrar" type="button" aria-label="Cerrar">×</button>'
        '<h2 id="quienes-titulo">¿Quiénes somos?</h2>'
        f'<div class="quienes-texto">{texto_quienes(config)}</div>'
        "</div></dialog>"
    )


MENU_SVG = (
    '<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
    'stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>'
)
MENU_JS = (
    "<script>(function(){var m=document.getElementById('menu-modulos'),b=document.querySelector('.menu-boton');"
    "if(!m||!b)return;"
    "b.addEventListener('click',function(){m.showModal();b.setAttribute('aria-expanded','true');});"
    "m.addEventListener('close',function(){b.setAttribute('aria-expanded','false');b.focus();});"
    "m.addEventListener('click',function(e){if(e.target===m||e.target.closest('.menu-cerrar'))m.close();});"
    "})();</script>"
)


def modulo_nav(actual, pedidos):
    """Barra del encabezado por módulo: botón de menú y título del módulo actual. El menú es un drawer
    (también en desktop) con los módulos. actual: "catalogo" o "pedidos". Sin catering activo no hay otro
    módulo y no hay menú."""
    titulo = "Catálogo" if actual == "catalogo" else NOMBRE_CATERING
    barra = f'<p class="modulo-titulo">{html.escape(titulo)}</p>'
    if not (pedidos or actual == "pedidos"):
        return f'<div class="envoltura modulo-barra">{barra}</div>'
    modulos = ((PAGINA_CATALOGO, "Catálogo", "catalogo"), (PAGINA_PEDIDOS, NOMBRE_CATERING, "pedidos"))
    actual_attr = ' aria-current="page"'
    enlaces = "".join(
        f'<li><a href="{href}"{actual_attr if clave == actual else ""}>{html.escape(nombre)}</a></li>'
        for href, nombre, clave in modulos
    )
    boton = (
        '<button class="menu-boton" type="button" aria-expanded="false" aria-controls="menu-modulos" '
        f'aria-label="Menú">{MENU_SVG}</button>'
    )
    drawer = (
        '<dialog class="menu-drawer" id="menu-modulos" aria-label="Menú">'
        '<button class="menu-cerrar" type="button" aria-label="Cerrar menú">×</button>'
        f'<nav aria-label="Secciones"><ul>{enlaces}</ul></nav></dialog>'
    )
    return f'<div class="envoltura modulo-barra">{boton}{barra}</div>{drawer}{MENU_JS}'


def redes(config, quienes=None, pedidos=False, pagina_actual=None):
    """Íconos del encabezado: ¿Quiénes somos? (modal o link a su página), Instagram (si está en config)
    y WhatsApp. Es el mismo conjunto en todas las páginas; el acceso al otro módulo es el botón
    de texto de modulo_nav, no un ícono. pagina_actual ("quienes") marca el botón de la página en la que se está."""
    botones = ""
    if quienes == "modal" and pagina_actual:
        # Fuera del catálogo no hay modal: el botón lleva al catálogo, que lo abre solo.
        botones = f'<a href="{PAGINA_CATALOGO}#quienes" aria-label="¿Quiénes somos?" title="¿Quiénes somos?">{QUIENES_SVG}</a>'
    elif quienes == "modal":
        botones = (
            '<button type="button" data-abrir-quienes aria-haspopup="dialog" aria-label="¿Quiénes somos?" '
            f'title="¿Quiénes somos?">{QUIENES_SVG}</button>'
        )
    elif quienes == "pagina":
        actual = ' aria-current="page"' if pagina_actual == "quienes" else ""
        botones = f'<a href="{PAGINA_QUIENES}"{actual} aria-label="¿Quiénes somos?" title="¿Quiénes somos?">{QUIENES_SVG}</a>'
    enlaces = []
    if config.get("instagram"):
        enlaces.append((config["instagram"], "Instagram", IG_SVG))
    enlaces.append((f"https://wa.me/{config['whatsapp']}", "WhatsApp", WA_SVG))
    return botones + "".join(
        f'<a href="{html.escape(url)}" target="_blank" rel="noopener" aria-label="{nombre}" title="{nombre}">'
        f'<svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">{svg}</svg></a>'
        for url, nombre, svg in enlaces
    )


def metadatos(config, titulo, ruta=""):
    """Canonical, Open Graph (vista previa al compartir el link) y datos estructurados para Google.

    ruta: la página dentro del sitio ("" es el catálogo). Los datos del negocio van solo en el catálogo.
    """
    if not config.get("dominio"):
        return ""
    base = f"https://{config['dominio'].strip()}/"
    url = base + ruta
    imagen = base + "assets/compartir.jpg"
    descripcion = config.get("descripcion") or config.get("eslogan", "")
    negocio = {
        "@context": "https://schema.org",
        "@type": "Store",
        "name": config["nombre"],
        "description": descripcion,
        "url": base,
        "logo": base + "assets/favicon-512.png",
        "image": imagen,
        "telephone": "+" + config["whatsapp"],
        "sameAs": [config["instagram"]] if config.get("instagram") else [],
    }
    etiquetas = [
        f'<link rel="canonical" href="{url}">',
        '<meta property="og:type" content="website">',
        '<meta property="og:locale" content="es_AR">',
        f'<meta property="og:site_name" content="{html.escape(config["nombre"])}">',
        f'<meta property="og:title" content="{html.escape(titulo)}">',
        f'<meta property="og:description" content="{html.escape(descripcion)}">',
        f'<meta property="og:url" content="{url}">',
        f'<meta property="og:image" content="{imagen}">',
        '<meta property="og:image:width" content="1200">',
        '<meta property="og:image:height" content="630">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if ruta:
        return "\n".join(etiquetas)
    etiquetas += [
        '<script type="application/ld+json">'
        + json.dumps(negocio, ensure_ascii=False).replace("</", "<\\/")
        + "</script>",
        # Nombre del sitio que muestra Google arriba del resultado (si no, pone el dominio)
        '<script type="application/ld+json">'
        + json.dumps(
            {
                "@context": "https://schema.org",
                "@type": "WebSite",
                "name": config["nombre"],
                "alternateName": config["dominio"].strip(),
                "url": base,
            },
            ensure_ascii=False,
        ).replace("</", "<\\/")
        + "</script>",
    ]
    return "\n".join(etiquetas)


def robots_y_sitemap(config, ahora, rutas):
    """robots.txt y sitemap.xml: le dicen a Google qué puede indexar y dónde están las páginas."""
    if not config.get("indexar"):
        (SALIDA / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
        return
    robots = "User-agent: *\nAllow: /\n"
    if config.get("dominio"):
        base = f"https://{config['dominio'].strip()}/"
        robots += f"\nSitemap: {base}sitemap.xml\n"
        (SALIDA / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "".join(f"  <url><loc>{base}{ruta}</loc><lastmod>{ahora.date().isoformat()}</lastmod></url>\n" for ruta in rutas)
            + "</urlset>\n"
        )
    (SALIDA / "robots.txt").write_text(robots)


UMBRAL_PISTA_CARRITO = 30  # unidades en el carrito a partir de las cuales se muestra la pista de Catering


def pista_carrito():
    """Aviso chico dentro del pedido flotante: aparece (por JS) solo cuando el carrito es muy grande."""
    return (
        f'<a class="pista-evento" id="pista-evento" href="{PAGINA_PEDIDOS}" hidden>'
        f'¿Es para un evento? Pedí presupuesto en {NOMBRE_CATERING}</a>'
    )


def texto_pie(config, ahora):
    """Texto del pie de las páginas de precios (catálogo y cotizador): una sola fuente para que no se desfasen."""
    pie = f" · {html.escape(config['pie'])}" if config.get("pie") else ""
    return f"Catálogo actualizado el {ahora.strftime('%d/%m/%Y %H:%M')}{pie}"


def pagina_pedidos(config, comunes, quienes):
    """Módulo opcional: cotizador de catering (invitados, opciones, extras, fecha y zona) que arma el
    estimado y el mensaje de WhatsApp, como el borrador original del cliente."""
    modulo = config["pedidos_especiales"]
    titulo = f"{NOMBRE_CATERING} | {config['nombre']}"
    datos = {
        "whatsapp": config["whatsapp"],
        "mensaje": modulo.get("mensaje", f"Hola! Quiero cotizar un catering con {config['nombre']}."),
        **leer_catering(config),
        "minimo_personas": modulo.get("minimo_personas", 1),
        "personas_por_defecto": modulo.get("personas_por_defecto", 0),
        "nota": modulo.get("nota", ""),
    }
    return rellenar(PAGINA_PEDIDOS, {
        **comunes,
        "{{FUENTES}}": link_fuentes(config, manuscrita=True),
        "{{TITULO}}": html.escape(titulo),
        "{{METADATOS}}": metadatos(config, titulo, PAGINA_PEDIDOS),
        "{{REDES}}": redes(config, quienes, True, "pedidos"),
        "{{MODULO}}": modulo_nav("pedidos", True),
        "{{PEDIDOS_TITULO}}": html.escape(NOMBRE_CATERING),
        "{{PEDIDOS_TEXTO}}": html.escape(modulo.get("texto", "")),
        "{{DATOS}}": json.dumps(datos, ensure_ascii=False).replace("</", "<\\/"),
    })


def rellenar(plantilla, reemplazos):
    """Lee plantilla/<plantilla> y cambia cada {{MARCA}} por su valor, en el orden del diccionario."""
    texto = (RAIZ / "plantilla" / plantilla).read_text(encoding="utf-8")
    # Encabezado compartido por todas las páginas.
    encabezado = (RAIZ / "plantilla" / "encabezado.html").read_text(encoding="utf-8").rstrip("\n")
    texto = texto.replace("{{ENCABEZADO}}", encabezado)
    for marca, valor in reemplazos.items():
        texto = texto.replace(marca, valor)
    return texto


def productos_publicados(config):
    """Los productos de la página que está online ahora, o None si no se pueden leer."""
    if not config.get("dominio"):
        return None
    url = f"https://{config['dominio'].strip()}/productos.json"
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:  # primera vez (todavía no existe), sin conexión, etc.
        print(f"No se pudo leer {url} ({e}). Se sigue sin comparar.")
        return None


def avisar_a_la_action(clave, valor):
    salida = os.environ.get("GITHUB_OUTPUT")
    if salida:
        with open(salida, "a") as f:
            f.write(f"{clave}={valor}\n")


def activa(variable):
    return os.environ.get(variable, "").strip().lower() == "true"


def main():
    config = leer_config()
    productos = limpiar_filas(leer_csv(config))
    revisar_fotos(productos)
    if not productos:
        sys.exit("ERROR: la planilla no tiene productos. No se publica nada para no dejar la página vacía.")

    anteriores = productos_publicados(config)
    if anteriores is not None:
        if activa("SOLO_SI_CAMBIA") and anteriores == productos:
            print("Los productos no cambiaron: no se publica.")
            avisar_a_la_action("publicar", "false")
            return
        if len(productos) < len(anteriores) * MINIMO_RESPECTO_ANTERIOR and not activa("FORZAR"):
            sys.exit(
                f"ERROR: la página tiene {len(anteriores)} productos y la planilla solo {len(productos)}. "
                "Si fue a propósito, corré la Action a mano tildando «Publicar igual». No se publica nada."
            )

    categorias = ordenar_categorias(productos, config)
    ahora = datetime.now(timezone(timedelta(hours=-3)))

    # Título de la pestaña y del resultado en Google: el nombre solo dice poco.
    titulo = config.get("titulo") or " | ".join(filter(None, [config["nombre"], config.get("eslogan")]))
    quienes = modo_quienes(config)
    print(f"¿Quiénes somos?: {quienes or 'oculto o sin texto en config.json, no se muestra'}")
    pedidos = pedidos_activo(config)
    print(f"Catering: {'activo' if pedidos else 'apagado'}")
    logo = config.get("logo", {})

    # Lo que comparten el catálogo y la página de ¿Quiénes somos?
    comunes = {
        "{{ESTILOS_BASE}}": estilos_marca(config) + (RAIZ / "plantilla" / "base.css").read_text(encoding="utf-8"),
        "{{FUENTES}}": link_fuentes(config),
        "{{LOGO}}": html.escape(logo.get("archivo", "assets/logo.png")),
        "{{LOGO_ANCHO}}": str(logo.get("ancho", 800)),
        "{{LOGO_ALTO}}": str(logo.get("alto", 300)),
        "{{NOMBRE}}": html.escape(config["nombre"]),
        "{{DESCRIPCION}}": html.escape(config.get("descripcion") or config.get("eslogan", "")),
        "{{SELLOS}}": sellos(config),
        "{{MODULO}}": "",
        "{{PIE}}": texto_pie(config, ahora),
        "{{ROBOTS}}": "" if config.get("indexar") else '<meta name="robots" content="noindex, nofollow">',
    }
    def marca(etiqueta, alt):
        imagen = (
            f'<img class="logo" src="{comunes["{{LOGO}}"]}" alt="{alt}" '
            f'width="{comunes["{{LOGO_ANCHO}}"]}" height="{comunes["{{LOGO_ALTO}}"]}">'
        )
        return f'<h1 class="marca">{imagen}</h1>' if etiqueta == "h1" else f'<a class="marca" href="./">{imagen}</a>'
    # En el catálogo el logo es el h1; en las demás páginas es el link de vuelta.
    comunes["{{MARCA}}"] = marca("a", comunes["{{NOMBRE}}"] + " — ir al catálogo")
    paginas = {"index.html": rellenar("index.html", {
        **comunes,
        "{{MARCA}}": marca("h1", comunes["{{NOMBRE}}"]),
        "{{TITULO}}": html.escape(titulo),
        "{{METADATOS}}": metadatos(config, titulo),
        "{{ESLOGAN}}": html.escape(config.get("eslogan", "")),
        "{{AVISO}}": html.escape(config.get("aviso", "")),
        "{{REDES}}": redes(config, quienes, pedidos),
        "{{MODULO}}": modulo_nav("catalogo", pedidos),
        "{{MODAL_QUIENES}}": modal_quienes(config) if quienes == "modal" else "",
        "{{PISTA_CARRITO}}": pista_carrito() if pedidos else "",
        "{{DATOS}}": json.dumps(
            {
                "productos": productos,
                "categorias": categorias,
                "whatsapp": config["whatsapp"],
                "mensaje": config.get("mensaje_pedido", "Hola, quiero hacer este pedido:"),
                "umbral_pista": config.get("pedidos_especiales", {}).get("umbral_pista", UMBRAL_PISTA_CARRITO),
                "emojis_producto": config.get("emojis_producto", {}),
                "emojis_categoria": config.get("emojis_categoria", {}),
                "emoji_por_defecto": config.get("emoji_por_defecto", "🛒"),
                # Categorías destacadas: si un producto está en una de estas, el mensaje lo marca.
                "repetidos": [c for c in categorias if normalizar(c) in {normalizar(x) for x in config.get("categorias_primero", [])}],
            },
            ensure_ascii=False,
        ).replace("</", "<\\/"),
    })}
    if quienes == "pagina":
        titulo_quienes = f"¿Quiénes somos? | {config['nombre']}"
        paginas[PAGINA_QUIENES] = rellenar(PAGINA_QUIENES, {
            **comunes,
            "{{TITULO}}": html.escape(titulo_quienes),
            "{{METADATOS}}": metadatos(config, titulo_quienes, PAGINA_QUIENES),
            "{{REDES}}": redes(config, quienes, pedidos, "quienes"),
            "{{QUIENES_TEXTO}}": texto_quienes(config),
        })
    if pedidos:
        paginas[PAGINA_PEDIDOS] = pagina_pedidos(config, comunes, quienes)

    if SALIDA.exists():
        shutil.rmtree(SALIDA)
    SALIDA.mkdir()
    for nombre, contenido in paginas.items():
        (SALIDA / nombre).write_text(contenido, encoding="utf-8")
    # Copia de los productos publicados: la próxima corrida la compara con la planilla.
    (SALIDA / "productos.json").write_text(json.dumps(productos, ensure_ascii=False), encoding="utf-8")
    shutil.copytree(RAIZ / "img", SALIDA / "img")
    shutil.copytree(RAIZ / "assets", SALIDA / "assets")
    # Google y algunos navegadores buscan el ícono en /favicon.ico aunque la página diga otra ruta
    shutil.copy(RAIZ / "assets" / "favicon.ico", SALIDA / "favicon.ico")

    robots_y_sitemap(config, ahora, ["" if nombre == "index.html" else nombre for nombre in paginas])

    avisar_a_la_action("publicar", "true")
    print(f"Listo: {len(productos)} productos en {len(categorias)} categorías -> _site/index.html")


if __name__ == "__main__":
    main()
