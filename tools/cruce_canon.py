#!/usr/bin/env python3
"""Cruce pedido por Santiago: formId incrustado en cada pagina (hero y modal) vs. a que
formulario apunta de verdad segun la API de HubSpot vs. el canon Piura (planilla, columna ID).

Regla: la herramienta gana sobre la hoja. Una diferencia entre el sitio y el canon es
DISCREPANCIA REAL solo si el formulario incrustado, resuelto por API, pertenece a otro programa.
Si el incrustado corresponde al programa de la pagina y el canon dice otra cosa, es FALSA ALARMA
DEL CANON (la planilla esta mal, el sitio esta bien).

Entradas: input/canon_piura.xlsx (hoja "Formularios de Google (Piura)"), output/10_paginas.json,
output/11_formularios.json, output/13_formularios_canon.json, output/20_matriz.json.
Salidas: output/cruce_canon_vicente.csv (80 filas), output/cruce_canon_discrepancias.csv,
output/21_cruce_canon.json.
"""
import sys, pathlib, csv, json, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs
import openpyxl

GUID = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")

def norm_url(u):
    return (u or "").strip().lower().rstrip("/").replace("http://", "https://").replace("https://www.", "https://")

# ---- canon ------------------------------------------------------------------------------
wb = openpyxl.load_workbook(hs.RAIZ / "input" / "canon_piura.xlsx", data_only=True)
ws = wb["Formularios de Google (Piura)"]
canon = []
for i, r in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
    tipo, nombre, idc, url = r[1], (r[2] or "").strip(), str(r[3] or "").strip(), (r[4] or "").strip()
    if not (nombre or idc or url):
        continue
    m = GUID.search(idc)
    canon.append({"fila": i, "tipo": tipo, "nombre": re.sub(r"\s+", " ", nombre.replace("​", "")),
                  "id_crudo": idc, "id": m.group(0) if m else None, "url": url, "url_norm": norm_url(url)})
# Si dos filas comparten URL, gana la que trae un formId valido (hay una fila duplicada con un id de Meta).
por_url = {}
for c in canon:
    if not c["url_norm"]:
        continue
    prev = por_url.get(c["url_norm"])
    if prev is None or (c["id"] and not prev["id"]):
        por_url[c["url_norm"]] = c
por_id = {}
for c in canon:
    if c["id"]:
        por_id.setdefault(c["id"], []).append(c)

pgs = {p["slug"]: p for p in hs.leer("10_paginas.json")["paginas"]}
forms = hs.leer("11_formularios.json")["formularios"]
extra = hs.leer("13_formularios_canon.json")["formularios"]
matriz = {f["slug"]: f for f in hs.leer("20_matriz.json")["filas"]}

def resolver(fid):
    """Nombre real segun HubSpot para cualquier formId (de las 40 o del canon)."""
    if fid in forms:
        return forms[fid]["nombre"], (forms[fid].get("valor_programa") or [None])[0]
    if fid in extra and extra[fid].get("http") == 200:
        return extra[fid]["nombre"], (extra[fid].get("valor_programa") or [None])[0]
    return None, None

filas, discrepancias, errores_canon = [], [], []
for pag in hs.paginas():
    slug, url = pag["slug"], pag["url"]
    w, m = pgs[slug], matriz[slug]
    fila_canon = por_url.get(norm_url(url))
    como = "url"
    if not fila_canon:
        # la URL del canon esta mal escrita o vacia: se busca por el ID incrustado
        cands = por_id.get(pag["form_id_esperado"], [])
        if cands:
            fila_canon, como = cands[0], "id (la URL del canon no coincide o esta vacia)"
    canon_id = fila_canon["id"] if fila_canon else None
    canon_nombre_api, _ = resolver(canon_id) if canon_id else (None, None)

    modal_ids = [i["formId"] for i in w["instancias"] if i["destino"] != "inline" and i["formId"]]
    instancias = [("hero", w.get("banner")), ("modal", modal_ids[-1] if modal_ids else None)]
    for inst, fid in instancias:
        nombre_api, programa_oculto = resolver(fid)
        corresponde = m["caso"] in ("A", "B")     # nombre real del form == programa de la pagina
        if not fila_canon:
            veredicto = "CANON SIN FILA"
            detalle = "la planilla no tiene fila para esta pagina"
        elif not canon_id:
            veredicto = "CANON SIN ID VALIDO"
            detalle = f"la planilla trae '{fila_canon['id_crudo']}' que no es un formId de HubSpot"
        elif fid == canon_id:
            veredicto = "COINCIDE"
            detalle = ""
        elif corresponde:
            veredicto = "FALSA ALARMA DEL CANON"
            detalle = (f"el sitio usa '{nombre_api}', que corresponde a la pagina; el canon dice {canon_id[:8]} "
                       f"= '{canon_nombre_api or 'no resuelto'}'")
        else:
            veredicto = "DISCREPANCIA REAL"
            detalle = f"el sitio usa '{nombre_api}', que es de otro programa"
        debe_quedar = fid if veredicto in ("COINCIDE", "FALSA ALARMA DEL CANON", "CANON SIN FILA", "CANON SIN ID VALIDO") else canon_id
        accion = "nada: el formId de la pagina es el correcto" if debe_quedar == fid else f"repuntar a {debe_quedar}"
        if veredicto == "FALSA ALARMA DEL CANON":
            accion += (f"; corregir la planilla (fila {fila_canon['fila']}): su ID {canon_id[:8]} resuelve a "
                       f"'{canon_nombre_api or 'no resuelto'}'")
        elif veredicto == "CANON SIN FILA":
            accion += "; agregar la fila a la planilla"
        r = {"pagina": slug, "url": url, "instancia": inst,
             "formId_en_la_pagina": fid,
             "apunta_hoy_a_nombre_real_hubspot": nombre_api,
             "programa_que_envia_el_formulario": programa_oculto or "",
             "formId_canon": canon_id or "", "nombre_en_canon": fila_canon["nombre"] if fila_canon else "",
             "fila_canon": fila_canon["fila"] if fila_canon else "", "canon_encontrado_por": como if fila_canon else "",
             "coincide_con_canon": "SI" if fid == canon_id else "NO",
             "veredicto": veredicto, "formId_que_debe_quedar": debe_quedar, "accion": accion, "detalle": detalle}
        filas.append(r)
        if veredicto == "DISCREPANCIA REAL":
            discrepancias.append(r)
        elif veredicto != "COINCIDE" and inst == "hero":
            errores_canon.append(r)

# Filas del canon que no corresponden a ninguna de las 40 paginas
usadas = {f["fila_canon"] for f in filas if f["fila_canon"]}
sobrantes = [{"fila": c["fila"], "nombre": c["nombre"], "id": c["id_crudo"], "url": c["url"]}
             for c in canon if c["fila"] not in usadas]

COLS = list(filas[0].keys())
with (hs.OUT / "cruce_canon_vicente.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(filas)
with (hs.OUT / "cruce_canon_discrepancias.csv").open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS); w.writeheader(); w.writerows(discrepancias)

import collections
res = {"generado": hs.ahora(), "instancias": len(filas),
       "veredictos": dict(collections.Counter(f["veredicto"] for f in filas)),
       "discrepancias_reales": discrepancias, "errores_del_canon": errores_canon,
       "filas_del_canon_sin_pagina": sobrantes}
print(hs.guardar("21_cruce_canon.json", res))
print("INSTANCIAS:", len(filas), "·", res["veredictos"])
print("DISCREPANCIAS REALES:", len(discrepancias))
print("ERRORES DEL CANON (por pagina):")
for e in errores_canon: print("  ", e["pagina"][:60], "|", e["veredicto"], "|", e["detalle"][:150])
print("FILAS DEL CANON SIN PAGINA:", [(s["fila"], s["nombre"][:40], s["id"][:12]) for s in sobrantes])
