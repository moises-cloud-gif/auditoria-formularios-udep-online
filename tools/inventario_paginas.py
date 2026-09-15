#!/usr/bin/env python3
"""Ronda 1. Reconfirma contra el sitio vivo el mapa de paginas y formularios."""
import sys, pathlib, re, requests
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

CREATE = re.compile(r"hbspt\.forms\.create\(\s*\{(.*?)\}\s*\)", re.S)
FID = re.compile(r'formId\s*:\s*["\']([0-9a-f-]{36})["\']')
TGT = re.compile(r'target\s*:\s*["\']([^"\']+)["\']')

res = {"generado": hs.ahora(), "paginas": [], "divergencias": []}

for pag in hs.paginas():
    try:
        html = requests.get(pag["url"], timeout=30).text
    except Exception as e:
        res["paginas"].append({"slug": pag["slug"], "error": str(e)[:120]})
        continue
    inst = []
    for c in CREATE.findall(html):
        m = FID.search(c)
        t = TGT.search(c)
        inst.append({"formId": m.group(1) if m else None,
                     "destino": t.group(1) if t else "inline"})
    ids = sorted({i["formId"] for i in inst if i["formId"]})
    fila = {
        "slug": pag["slug"], "url": pag["url"],
        "llamadas_create": len(inst),
        "form_ids": ids,
        "banner": next((i["formId"] for i in inst if i["destino"] == "inline"), None),
        "modal": next((i["formId"] for i in inst if i["destino"] != "inline"), None),
        "recaptcha_prueba_en_html": "for testing purposes only" in html.lower(),
        "titulo_wordpress": "QUIERES MÁS INFORMACIÓN" in html.upper(),
        "anomalia": None if len(inst) == 2 and len(ids) == 1 else f"{len(inst)} incrustaciones / {len(ids)} formularios",
    }
    if pag.get("form_id_esperado") and ids and pag["form_id_esperado"] not in ids:
        res["divergencias"].append({"slug": pag["slug"], "esperado": pag["form_id_esperado"], "hallado": ids})
    res["paginas"].append(fila)
    print(f"{pag['slug']}: {len(inst)} incrustaciones, {len(ids)} formulario(s)")

print(hs.guardar("10_paginas.json", res))
print(f"PAGINAS: {len(res['paginas'])}/40 · DIVERGENCIAS: {len(res['divergencias'])}")
