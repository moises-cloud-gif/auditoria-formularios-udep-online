#!/usr/bin/env python3
"""Ronda 1. Mapa formId -> workflow Activador.

Recorre todos los flows del portal y busca los 40 formId de UDEP dentro de la
definicion de cada uno. De los flows que referencian algun formId guarda la
respuesta cruda en output/evidencia/flows/<flowId>.json y anota si la referencia
esta en los criterios de inscripcion (enrollmentCriteria) o en otra parte.
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

RAW = hs.EVID / "flows"
RAW.mkdir(parents=True, exist_ok=True)

fids = {p["form_id_esperado"]: p["slug"] for p in hs.paginas() if p.get("form_id_esperado")}
mapa = {f: [] for f in fids}
flows_con_udep = {}
revisados = 0
errores_detalle = 0
after = None

while True:
    ruta = "/automation/v4/flows?limit=100" + (f"&after={after}" if after else "")
    r = hs.api("GET", ruta)
    if r.status_code != 200:
        print(f"ERROR al listar flows: HTTP {r.status_code} — {r.text[:200]}")
        break
    j = r.json()
    for f in j.get("results", []):
        revisados += 1
        det = hs.api("GET", f"/automation/v4/flows/{f['id']}")
        if det.status_code != 200:
            errores_detalle += 1
            continue
        dj = det.json()
        crudo = json.dumps(dj)
        hallados = [fid for fid in fids if fid in crudo]
        if not hallados:
            continue
        (RAW / f"{f['id']}.json").write_text(json.dumps(dj, ensure_ascii=False, indent=2), encoding="utf-8")
        enrol = json.dumps(dj.get("enrollmentCriteria") or {})
        flows_con_udep[str(f["id"])] = {
            "nombre": dj.get("name"), "activo": dj.get("isEnabled"), "tipo": dj.get("type"),
            "objeto": dj.get("objectTypeId"), "form_ids_referenciados": hallados,
            "cantidad_form_ids_udep": len(hallados),
        }
        for fid in hallados:
            mapa[fid].append({"flowId": str(f["id"]), "nombre": dj.get("name"),
                              "activo": dj.get("isEnabled"),
                              "en_criterios_de_inscripcion": fid in enrol})
    after = (j.get("paging", {}).get("next", {}) or {}).get("after")
    if not after:
        break

res = {"generado": hs.ahora(), "flows_revisados": revisados,
       "flows_sin_detalle": errores_detalle, "flows_con_formularios_udep": flows_con_udep, "mapa": {}}
for fid, slug in fids.items():
    act = mapa[fid]
    res["mapa"][fid] = {
        "slug": slug, "activadores": act,
        "estado": "SIN_ACTIVADOR" if not act else ("UNO" if len(act) == 1 else "MAS_DE_UNO"),
    }

print(hs.guardar("12_activadores.json", res))
sin = [v["slug"] for v in res["mapa"].values() if v["estado"] == "SIN_ACTIVADOR"]
mult = [v["slug"] for v in res["mapa"].values() if v["estado"] == "MAS_DE_UNO"]
print(f"FLOWS REVISADOS: {revisados} · FLOWS CON FORMULARIOS UDEP: {len(flows_con_udep)}")
print(f"SIN ACTIVADOR ({len(sin)}): {sin}")
print(f"CON MAS DE UNO ({len(mult)}): {mult}")
