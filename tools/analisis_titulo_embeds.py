#!/usr/bin/env python3
"""Titulo duplicado y variantes de incrustacion, a partir del HTML crudo de las 40 paginas y de la
definicion de los formularios por API. Cruza con el QA visual de agosto (planilla canon, Hoja 7).

Por pagina: cuantas veces aparece el titulo de WordPress y donde (hero / modal), si hay CSS que
oculte el encabezado del formulario de HubSpot, si el formulario trae encabezado propio hoy, y la
"firma" del codigo de incrustacion (para detectar el embed nuevo). Sale output/41_titulo_embeds.json.
"""
import sys, pathlib, re, json, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs
import openpyxl

TITULO = re.compile(r"QUIERES\s+M[AÁ]S\s+INFORMACI[OÓ]N", re.I)
CSS_OCULTA = re.compile(r"(#inscripcion|\.hs-richtext|hs-form[^{]*h1|hbspt-form[^{]*h1|\.hs_cos_wrapper[^{]*h1)[^{]*\{[^}]*display\s*:\s*none", re.I | re.S)
CSS_CUALQUIER = re.compile(r"(#inscripcion|\.hs-richtext)[^{}]*\{[^}]*\}", re.I | re.S)
CREATE = re.compile(r"hbspt\.forms\.create\(\s*\{(.*?)\}\s*\)", re.S)

pgs = {p["slug"]: p for p in hs.leer("10_paginas.json")["paginas"]}
forms = hs.leer("11_formularios.json")["formularios"]

# QA de agosto (Hoja 7): slug -> observacion
wb = openpyxl.load_workbook(hs.RAIZ / "input" / "canon_piura.xlsx", data_only=True)
agosto = {}
for r in wb["Hoja 7"].iter_rows(min_row=2, values_only=True):
    if r[0]:
        agosto[str(r[0]).strip()] = {"estado": r[2], "observacion": r[3]}

res = {"generado": hs.ahora(), "paginas": []}
for pag in hs.paginas():
    slug = pag["slug"]
    html = (hs.EVID / "paginas" / f"{slug}.html").read_text(encoding="utf-8", errors="replace")
    titulos = [m.start() for m in TITULO.finditer(html)]
    # posicion del modal en el HTML
    pos_modal = html.find("hubspot-formulario")
    pos_modal_ini = html.rfind("<div", 0, pos_modal) if pos_modal > 0 else -1
    en_modal = sum(1 for t in titulos if pos_modal > 0 and abs(t - pos_modal) < 3000 and t > pos_modal - 3000)
    firmas = []
    for c in CREATE.findall(html):
        c2 = re.sub(r"\s+", " ", c)
        firmas.append(("css" if "css" in c2 else "") + ("+onFormReady" if "onFormReady" in c2 else "") or "plano")
    f = forms.get(pag["form_id_esperado"], {})
    a = agosto.get(slug, {})
    fila = {
        "slug": slug,
        "titulo_wp_ocurrencias_html": len(titulos),
        "titulo_wp_cerca_del_modal": en_modal,
        "css_oculta_encabezado_hubspot": bool(CSS_OCULTA.search(html)),
        "css_menciona_encabezado": [re.sub(r"\s+", " ", m.group(0))[:160] for m in CSS_CUALQUIER.finditer(html)][:3],
        "formulario_trae_encabezado_hoy": f.get("tiene_encabezado"),
        "formulario_actualizado": (f.get("actualizado") or "")[:10],
        "firma_incrustaciones": firmas,
        "agosto_estado": a.get("estado"), "agosto_observacion": a.get("observacion"),
        "agosto_decia_titulo_duplicado_modal": bool(a.get("observacion") and "DUPLICADO" in a["observacion"]),
        "agosto_decia_titulo_ausente_hero": bool(a.get("observacion") and "AUSENTE" in a["observacion"]),
    }
    # riesgo estructural hoy: WP trae titulo + HubSpot trae encabezado + no hay CSS que lo oculte
    fila["riesgo_duplicado_hoy"] = bool(titulos) and bool(f.get("tiene_encabezado")) and not fila["css_oculta_encabezado_hubspot"]
    res["paginas"].append(fila)

P = res["paginas"]
res["resumen"] = {
    "paginas_con_titulo_wp_en_html": sum(1 for p in P if p["titulo_wp_ocurrencias_html"]),
    "distribucion_ocurrencias_titulo_wp": dict(collections.Counter(p["titulo_wp_ocurrencias_html"] for p in P)),
    "paginas_con_css_que_oculta_encabezado": sum(1 for p in P if p["css_oculta_encabezado_hubspot"]),
    "formularios_con_encabezado_hoy": sum(1 for p in P if p["formulario_trae_encabezado_hoy"]),
    "riesgo_duplicado_hoy": [p["slug"] for p in P if p["riesgo_duplicado_hoy"]],
    "agosto_duplicado_en_modal": [p["slug"] for p in P if p["agosto_decia_titulo_duplicado_modal"]],
    "agosto_ausente_en_hero": [p["slug"] for p in P if p["agosto_decia_titulo_ausente_hero"]],
    "firmas_incrustacion": dict(collections.Counter(tuple(p["firma_incrustaciones"]) and "|".join(p["firma_incrustaciones"]) for p in P)),
}
print(hs.guardar("41_titulo_embeds.json", res))
print(json.dumps(res["resumen"], ensure_ascii=False, indent=1))
