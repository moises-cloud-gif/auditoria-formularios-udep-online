#!/usr/bin/env python3
"""Ronda 2, parte mecanica. Cruza los tres inventarios y deja la matriz de 40 filas
con todo lo objetivo resuelto. La rama A/B/C/D final la decide el agente clasificador,
porque el caso C exige saber si el formulario del programa existe en otra pagina.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

pgs = {p["slug"]: p for p in hs.leer("10_paginas.json")["paginas"]}
forms = hs.leer("11_formularios.json")["formularios"]
act = hs.leer("12_activadores.json")["mapa"]

import json
_pl = json.loads((pathlib.Path(__file__).parents[1] / "input" / "plantilla_referencia.json")
                 .read_text(encoding="utf-8"))
PLANTILLA = [c["nombre"] for c in _pl["campos"]]

filas = []
for pag in hs.paginas():
    slug = pag["slug"]
    web = pgs.get(slug, {})
    fid = web.get("banner") or pag.get("form_id_esperado")
    f = forms.get(fid, {})
    nombres = [c["nombre"] for c in f.get("campos", [])]
    filas.append({
        "slug": slug,
        "tipo": pag["tipo"],
        "form_id": fid,
        "banner_y_modal_iguales": web.get("banner") == web.get("modal"),
        "nombre_formulario": f.get("nombre"),
        "campos": nombres,
        "faltan_de_plantilla": [c for c in PLANTILLA if c not in nombres],
        "sobran_sobre_plantilla": [c for c in nombres if c not in PLANTILLA],
        "propiedades_sin_sufijo": f.get("sin_sufijo", []),
        "tiene_clausula_datos": f.get("tiene_clausula_datos"),
        "unidad_de_negocio": f.get("unidad_de_negocio"),
        "activadores": act.get(fid, {}).get("activadores", []),
        "estado_activador": act.get(fid, {}).get("estado", "DESCONOCIDO"),
        "anomalia_marcado": web.get("anomalia"),
        "recaptcha_prueba": web.get("recaptcha_prueba_en_html"),
        "caso": None,          # lo decide el agente
        "severidad_max": None, # lo decide el agente
        "accion": None,        # lo decide el agente
    })

print(hs.guardar("20_matriz.json", {"generado": hs.ahora(), "filas": filas}))
print(f"MATRIZ: {len(filas)} filas · listas para clasificar")
print("Sin sufijo:", sum(1 for f in filas if f["propiedades_sin_sufijo"]))
print("Sin activador:", sum(1 for f in filas if f["estado_activador"] == "SIN_ACTIVADOR"))
