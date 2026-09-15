#!/usr/bin/env python3
"""Ronda 2. Cruza los tres inventarios y clasifica las 40 paginas segun CA-3 y §4.4.

Todo lo objetivo sale de output/10_, 11_ y 12_. Lo unico que aporta criterio humano es
la tabla PROGRAMA_ESPERADO (que opcion del desplegable oculto corresponde a cada pagina)
y la tabla CLUSTER_REVISAR (Activadores cuyo nombre no cuadra con el programa). Ambas
estan a la vista para que se puedan discutir.
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

pgs = {p["slug"]: p for p in hs.leer("10_paginas.json")["paginas"]}
forms = hs.leer("11_formularios.json")["formularios"]
act = hs.leer("12_activadores.json")["mapa"]

_pl = json.loads((pathlib.Path(__file__).parents[1] / "input" / "plantilla_referencia.json")
                 .read_text(encoding="utf-8"))
PLANTILLA = _pl["campos"]                      # nombre, etiqueta, obligatorio, oculto
NOMBRES_PLANTILLA = [c["nombre"] for c in PLANTILLA]
MENSAJE_OK = _pl["mensaje_al_enviar"].strip()

# Que valor deberia traer el campo oculto de programa en cada pagina. Se toma de la lista
# de opciones real de la propiedad (11_formularios). None = no existe opcion para ese programa.
PROGRAMA_ESPERADO = {
    "curso-de-analitica-digital-growth-marketing": None,   # no hay opcion en cursos_piura__udn_udep_
    "curso-de-business-intelligence-data-science": "Business Intelligence & Data Science",
    "curso-de-coaching": "Coaching",
    "curso-de-comunicacion-efectiva": "Comunicación Efectiva",
    "curso-de-digital-business-model": "Digital Business Model",
    "curso-de-felicidad-y-bienestar-organizacional": "Felicidad y Bienestar Organizacional",
    "curso-de-gestion-de-equipos-de-alto-rendimiento": "Gestión de Equipos de Alto Rendimiento",
    "curso-de-gestion-del-talento": "Gestión del Talento",
    "curso-de-inteligencia-emocional": "Inteligencia Emocional",
    "curso-de-liderazgo-en-la-era-digital": "Liderazgo en la era digital",
    "curso-de-marketing-digital": "Marketing Digital",
    "curso-de-negociacion-y-resolucion-de-conflictos": "Negociación y Resolución de Conflictos",
    "curso-de-negocios-e-commerce": "Negocios e-commerce",   # existen 3 variantes: ver observacion
    "curso-de-negocios-innovadores": "Negocios Innovadores",
    "curso-de-transformacion-digital": "Transformación Digital",
    "curso-desarrollo-organizacional-y-gestion-del-cambio": "Desarrollo Organizacional y Gestión del Cambio",
    "diplomado-en-gestion-de-la-felicidad-y-bienestar-organizacional": "Diplomado Gestión Felicidad y Bienestar Organizacional",
    "diplomado-en-habilidades-para-la-gestion-de-equipos": "Diplomado Habilidades para la Gestión de Equipos",
    "diplomado-en-inteligencia-emocional-y-coaching-para-el-liderazgo-en-las-organizaciones": "Diplomado Inteligencia Emocional & Coaching",
    "diplomado-en-liderazgo-y-gestion-del-talento": "Diplomado Liderazgo y Gestión del Talento",
    "diplomado-en-marketing-digital-y-analitica": "Diplomado Marketing Digital y Analítica",
    "diplomado-en-marketing-digital-y-ecommerce": "Diplomado en Marketing Digital y Ecommerce",
    "programa-de-especializacion-en-comunicacion-efectiva-y-gestion-de-equipos-de-alto-rendimiento": "Comunicación Efectiva y Gestión de Equipos de Alto Rendimiento",
    "programa-de-especializacion-en-comunicacion-efectiva-y-gestion-del-talento": "Comunicación Efectiva y Gestión del Talento",
    "programa-de-especializacion-en-felicidad-organizacional-y-gestion-de-equipos-de-alto-rendimiento": "Felicidad Organizacional y Gestion de Equipos de Alto Rendimiento",
    "programa-de-especializacion-en-felicidad-organizacional-y-inteligencia-emocional": "Felicidad Organizacional e Inteligencia Emocional",
    "programa-de-especializacion-en-felicidad-y-desarrollo-organizacional": "Felicidad y Desarrollo Organizacional",
    "programa-de-especializacion-en-gestion-del-cambio-y-negociacion-de-conflictos": "Gestión del Cambio y Negociación de Conflictos",
    "programa-de-especializacion-en-gestion-del-talento-y-negociacion-de-conflictos": "Gestión de Talento y Negociación de Conflictos",
    "programa-de-especializacion-en-habilidades-para-la-gestion-de-equipos": "Habilidades para la Gestión de Equipos",
    "programa-de-especializacion-en-inteligencia-emocional-y-coaching": "Inteligencia Emocional y Coaching",
    "programa-de-especializacion-en-liderazgo-y-comunicacion-efectiva": "Liderazgo y Comunicación Efectiva",
    "programa-de-especializacion-en-liderazgo-y-felicidad-organizacional": "liderazgo_y_felicidad_organizacional",
    "programa-de-especializacion-en-liderazgo-y-gestion-del-talento": "Liderazgo y Gestión del Talento",
    "programa-de-especializacion-en-liderazgo-y-negociacion-de-conflictos": "Liderazgo y Negociación de Conflictos",
    "programa-de-especializacion-en-liderazgo-y-transformacion-digital": "liderazgo_y_transformacion_digital",
    "programa-de-especializacion-en-marketing-digital-y-business-model": "Marketing Digital y Business Model",
    "programa-de-especializacion-en-marketing-digital-y-e-commerce": "Marketing Digital y Ecommerce",
    "programa-de-especializacion-en-modelo-de-negocios-digitales-y-business-intelligence": "Modelo de Negocios Digitales y Business Intelligence",
    "programa-de-especializacion-en-modelo-de-negocios-y-transformacion-digital": "Modelo de Negocios y Transformación Digital",
}

# Activadores de cluster cuyo nombre no cuadra a simple vista con el programa de la pagina.
CLUSTER_REVISAR = {
    "diplomado-en-marketing-digital-y-ecommerce":
        "Es diplomado pero entra por el Activador del cluster Marketing Digital, no por el de Diplomados. Puede ser intencional.",
    "programa-de-especializacion-en-gestion-del-cambio-y-negociacion-de-conflictos":
        "Entra por el cluster Emprendimiento, Innovación y Tecnología; por tema corresponderia a Habilidades de Gestión.",
}

ORDEN = {"CRITICO": 4, "ALTO": 3, "MEDIO": 2, "BAJO": 1, None: 0}


def peor(a, b):
    return a if ORDEN[a] >= ORDEN[b] else b


filas = []
for pag in hs.paginas():
    slug = pag["slug"]
    web = pgs.get(slug, {})
    fid = web.get("banner") or pag.get("form_id_esperado")
    f = forms.get(fid, {})
    campos = f.get("campos", [])
    nombres = [c["nombre"] for c in campos]
    hallazgos = []          # (id_check, severidad, texto)
    es_programa = pag["tipo"] in ("programa", "diplomado")

    # ---- H7: definicion contra la plantilla -------------------------------------------
    # Los programas y diplomados usan programas_piura__udn_udep_ en lugar de cursos_piura__udn_udep_.
    # Se acepta como variante (propiedad distinta para otro tipo de producto) y se anota.
    esperados = [("programas_piura__udn_udep_" if es_programa and n == "cursos_piura__udn_udep_" else n)
                 for n in NOMBRES_PLANTILLA]
    if nombres != esperados:
        faltan = [n for n in esperados if n not in nombres]
        sobran = [n for n in nombres if n not in esperados]
        if faltan or sobran:
            sev = "CRITICO" if any(s in ("message", "cursos_piura", "medio_de_contacto", "nivel_de_estudios")
                                   for s in sobran) else "MEDIO"
            hallazgos.append(("H7", sev, f"propiedades distintas a la plantilla: faltan {faltan}, sobran {sobran}"))
        else:
            hallazgos.append(("H7", "MEDIO", "mismos campos que la plantilla pero en otro orden"))
    for c in campos:
        ref = next((p for p in PLANTILLA if p["nombre"] == c["nombre"]
                    or (es_programa and p["nombre"] == "cursos_piura__udn_udep_" and c["nombre"] == "programas_piura__udn_udep_")), None)
        if not ref:
            continue
        if (c["etiqueta"] or "").strip() != ref["etiqueta"] and not (es_programa and c["nombre"].startswith("programas_piura")):
            hallazgos.append(("H7", "MEDIO", f"etiqueta de {c['nombre']}: '{c['etiqueta']}' (plantilla: '{ref['etiqueta']}')"))
        if bool(c["obligatorio"]) != bool(ref["obligatorio"]):
            hallazgos.append(("H7", "MEDIO", f"obligatoriedad de {c['nombre']}: {c['obligatorio']} (plantilla: {ref['obligatorio']})"))
    if f.get("sin_sufijo"):
        hallazgos.append(("H7", "CRITICO", f"propiedad sin sufijo __udn_udep_: {f['sin_sufijo']}"))
    if f.get("usa_message_generico"):
        hallazgos.append(("H7", "CRITICO", "escribe en la propiedad generica 'message' en vez de 'mensaje': el dato no llega junto al del resto"))
    if f and not f.get("tiene_clausula_datos"):
        hallazgos.append(("R5", "ALTO", "sin clausula de autorizacion de datos"))
    if f and not f.get("tiene_encabezado"):
        hallazgos.append(("H7", "BAJO", "sin encabezado '¿QUIERES MÁS INFORMACIÓN?' en el formulario"))
    msg = (f.get("mensaje_confirmacion") or {}).get("value") or ""
    if f and MENSAJE_OK.lower() not in msg.lower():
        hallazgos.append(("R4", "ALTO", f"mensaje de confirmacion distinto o vacio: '{msg[:60]}'"))

    # ---- H3: programa -----------------------------------------------------------------
    esperado = PROGRAMA_ESPERADO.get(slug)
    valor = (f.get("valor_programa") or [None])[0]
    h3 = None
    if f:
        if esperado is None:
            h3 = "SIN_OPCION"
            hallazgos.append(("H3", "CRITICO", f"la propiedad de programa no tiene una opcion para este programa; el formulario envia '{valor}'"))
        elif valor is None:
            h3 = "SIN_VALOR"
            hallazgos.append(("H3", "CRITICO", "el campo oculto de programa no tiene valor por defecto: el lead entra sin programa"))
        elif valor != esperado:
            h3 = "OTRO_PROGRAMA"
            hallazgos.append(("H3", "CRITICO", f"el campo oculto envia '{valor}' y la pagina es de '{esperado}'"))
        else:
            h3 = "OK"

    # ---- H4: activador ----------------------------------------------------------------
    a = act.get(fid, {})
    estado_act = a.get("estado", "DESCONOCIDO")
    if estado_act == "SIN_ACTIVADOR":
        hallazgos.append(("H4", "CRITICO", "ningun workflow Activador referencia este formulario: el lead no se asigna"))
    elif estado_act == "MAS_DE_UNO":
        hallazgos.append(("H4", "CRITICO", f"{len(a.get('activadores', []))} Activadores referencian el formulario"))
    if slug in CLUSTER_REVISAR:
        hallazgos.append(("H4", "MEDIO", "REVISAR: " + CLUSTER_REVISAR[slug]))

    # ---- marcado del sitio ------------------------------------------------------------
    if web.get("anomalia"):
        hallazgos.append(("CA-7", "ALTO", f"marcado de WordPress: {web['anomalia']}"))

    # ---- caso CA-3 --------------------------------------------------------------------
    # El nombre del formulario corresponde a la pagina en los 40 (11_formularios): no hay C ni D.
    corresponde = bool(f) and slug in PROGRAMA_ESPERADO
    problemas_definicion = [h for h in hallazgos if h[0] in ("H3", "H7", "R4", "R5")]
    if not f:
        caso, accion, quien = None, "sin definicion del formulario: no se puede clasificar", None
    elif not corresponde:
        caso, accion, quien = "C/D", "revisar a mano", None
    elif problemas_definicion:
        caso, accion, quien = "B", "editar el formulario en HubSpot (no cambia el formId)", "5minutos"
    else:
        caso, accion, quien = "A", "nada", None

    sev_max = None
    for h in hallazgos:
        sev_max = peor(sev_max, h[1])

    filas.append({
        "slug": slug, "tipo": pag["tipo"], "url": pag["url"],
        "form_id": fid, "form_id_en_pagina": web.get("form_ids"),
        "banner_y_modal_iguales": web.get("banner") == web.get("modal") or (web.get("llamadas_create") == 8),
        "nombre_formulario": f.get("nombre"),
        "campos": nombres,
        "campo_oculto_programa": f.get("campo_oculto_programa"),
        "programa_enviado": valor, "programa_esperado": esperado, "H3": h3,
        "propiedades_sin_sufijo": f.get("sin_sufijo", []),
        "usa_message_generico": f.get("usa_message_generico"),
        "tiene_clausula_datos": f.get("tiene_clausula_datos"),
        "tiene_encabezado": f.get("tiene_encabezado"),
        "mensaje_confirmacion": msg,
        "recaptcha_habilitado": f.get("recaptcha_habilitado"),
        "unidad_de_negocio": f.get("unidad_de_negocio"),
        "H6": "NO_VERIFICABLE_POR_API",
        "activadores": a.get("activadores", []), "estado_activador": estado_act,
        "H4": "OK" if estado_act == "UNO" and slug not in CLUSTER_REVISAR else ("REVISAR" if estado_act == "UNO" else estado_act),
        "anomalia_marcado": web.get("anomalia"),
        "hallazgos": [{"check": h[0], "severidad": h[1], "detalle": h[2]} for h in hallazgos],
        "severidad_max": sev_max,
        "caso": caso, "accion": accion, "quien": quien,
        "actualizado_en_hubspot": f.get("actualizado"),
    })

import collections
res = {"generado": hs.ahora(), "filas": filas,
       "reparto": dict(collections.Counter(x["caso"] for x in filas)),
       "severidad": dict(collections.Counter(x["severidad_max"] for x in filas)),
       "H3": dict(collections.Counter(x["H3"] for x in filas)),
       "H4": dict(collections.Counter(x["H4"] for x in filas))}
print(hs.guardar("20_matriz.json", res))
print(f"MATRIZ: {len(filas)} filas")
print("CASOS:", res["reparto"])
print("SEVERIDAD MAX:", res["severidad"])
print("H3 programa:", res["H3"])
print("H4 activador:", res["H4"])
