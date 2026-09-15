#!/usr/bin/env python3
"""Ronda 1. Mapa formId -> workflow Activador."""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

fids = {p["form_id_esperado"]: p["slug"] for p in hs.paginas() if p.get("form_id_esperado")}
mapa = {f: [] for f in fids}
revisados = 0
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
            continue
        crudo = json.dumps(det.json())
        for fid in fids:
            if fid in crudo:
                mapa[fid].append({"flowId": f["id"], "nombre": f.get("name"),
                                  "activo": f.get("isEnabled")})
    after = (j.get("paging", {}).get("next", {}) or {}).get("after")
    if not after:
        break

res = {"generado": hs.ahora(), "flows_revisados": revisados, "mapa": {}}
for fid, slug in fids.items():
    act = mapa[fid]
    res["mapa"][fid] = {
        "slug": slug, "activadores": act,
        "estado": "SIN_ACTIVADOR" if not act else ("UNO" if len(act) == 1 else "MAS_DE_UNO"),
    }

print(hs.guardar("12_activadores.json", res))
sin = [v["slug"] for v in res["mapa"].values() if v["estado"] == "SIN_ACTIVADOR"]
mult = [v["slug"] for v in res["mapa"].values() if v["estado"] == "MAS_DE_UNO"]
print(f"FLOWS REVISADOS: {revisados}")
print(f"SIN ACTIVADOR ({len(sin)}): {sin}")
print(f"CON MAS DE UNO ({len(mult)}): {mult}")
