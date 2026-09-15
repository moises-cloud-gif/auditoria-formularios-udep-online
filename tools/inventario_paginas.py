#!/usr/bin/env python3
"""Ronda 1. Reconfirma contra el sitio vivo el mapa de paginas y formularios.

Ademas del formId y el destino de cada incrustacion, guarda el cuerpo completo de
cada llamada hbspt.forms.create (para ver si el sitio manipula campos ocultos con
onFormReady u otros callbacks), busca en el HTML referencias a las propiedades de
programa, y guarda el HTML crudo en output/evidencia/paginas/<slug>.html.
"""
import sys, pathlib, re, requests
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

CREATE = re.compile(r"hbspt\.forms\.create\(\s*\{(.*?)\}\s*\)", re.S)
FID = re.compile(r'formId\s*:\s*["\']([0-9a-f-]{36})["\']')
TGT = re.compile(r'target\s*:\s*["\']([^"\']+)["\']')
PORTAL = re.compile(r'portalId\s*:\s*["\']?(\d+)')

RAW = hs.EVID / "paginas"
RAW.mkdir(parents=True, exist_ok=True)

res = {"generado": hs.ahora(), "paginas": [], "divergencias": [], "paginas_extra": []}

for pag in hs.paginas():
    try:
        rr = requests.get(pag["url"], timeout=30)
        html = rr.text
    except Exception as e:
        res["paginas"].append({"slug": pag["slug"], "error": str(e)[:120]})
        continue
    (RAW / f"{pag['slug']}.html").write_text(html, encoding="utf-8")
    inst = []
    for c in CREATE.findall(html):
        m = FID.search(c)
        t = TGT.search(c)
        p = PORTAL.search(c)
        inst.append({"formId": m.group(1) if m else None,
                     "destino": t.group(1) if t else "inline",
                     "portalId": p.group(1) if p else None,
                     "tiene_callbacks": bool(re.search(r"onForm(Ready|Submit|Submitted)", c)),
                     "cuerpo": re.sub(r"\s+", " ", c).strip()[:600]})
    ids = sorted({i["formId"] for i in inst if i["formId"]})
    fila = {
        "slug": pag["slug"], "url": pag["url"], "http": rr.status_code,
        "llamadas_create": len(inst),
        "form_ids": ids,
        "portal_ids": sorted({i["portalId"] for i in inst if i["portalId"]}),
        "banner": next((i["formId"] for i in inst if i["destino"] == "inline"), None),
        "modal": next((i["formId"] for i in inst if i["destino"] != "inline"), None),
        "instancias": inst,
        "html_manipula_campo_programa": bool(re.search(r"cursos_piura|programas_piura", html)),
        "html_menciona_recaptcha": bool(re.search(r"recaptcha|grecaptcha", html, re.I)),
        "recaptcha_prueba_en_html": "for testing purposes only" in html.lower(),
        "titulo_wordpress": "QUIERES MÁS INFORMACIÓN" in html.upper(),
        "anomalia": None if len(inst) == 2 and len(ids) == 1 else f"{len(inst)} incrustaciones / {len(ids)} formularios",
    }
    if pag.get("form_id_esperado") and ids and pag["form_id_esperado"] not in ids:
        res["divergencias"].append({"slug": pag["slug"], "esperado": pag["form_id_esperado"], "hallado": ids})
    res["paginas"].append(fila)
    print(f"{pag['slug']}: {len(inst)} incrustaciones, {len(ids)} formulario(s)")

# Pagina fuera del inventario que el requerimiento pide reportar (seccion 2).
for extra in ("https://udeponline.pe/programas-de-especializacion-dev/",):
    try:
        e = requests.get(extra, timeout=30)
        ids = sorted(set(FID.findall(e.text)))
        res["paginas_extra"].append({"url": extra, "http": e.status_code, "form_ids": ids,
                                     "publicada": e.status_code == 200})
    except Exception as ex:
        res["paginas_extra"].append({"url": extra, "error": str(ex)[:120]})

print(hs.guardar("10_paginas.json", res))
print(f"PAGINAS: {len(res['paginas'])}/40 · DIVERGENCIAS: {len(res['divergencias'])}")
