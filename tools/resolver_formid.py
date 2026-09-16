#!/usr/bin/env python3
"""Resuelve por API formIds que no estan en las 40 paginas (por ejemplo, los que trae el canon
Piura y el sitio no usa). GET /marketing/v3/forms/{id}; guarda la respuesta cruda en
output/evidencia/formularios/<id>.json y un resumen en output/13_formularios_canon.json.

Uso: python3 tools/resolver_formid.py <formId> [<formId> ...]
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

RAW = hs.EVID / "formularios"
RAW.mkdir(parents=True, exist_ok=True)
try:
    res = hs.leer("13_formularios_canon.json")
except FileNotFoundError:
    res = {"formularios": {}}
res["generado"] = hs.ahora()

for fid in sys.argv[1:]:
    r = hs.api("GET", f"/marketing/v3/forms/{fid}")
    if r.status_code != 200:
        res["formularios"][fid] = {"http": r.status_code, "cuerpo": r.text[:300]}
        print(f"{fid}: HTTP {r.status_code}")
        continue
    j = r.json()
    (RAW / f"{fid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")
    oculto = next((c for g in j.get("fieldGroups", []) for c in g.get("fields", [])
                   if c.get("hidden") and (c.get("name") or "").startswith(("cursos_piura", "programas_piura"))), None)
    res["formularios"][fid] = {
        "http": 200, "nombre": j.get("name"), "archivado": j.get("archived"),
        "creado": j.get("createdAt"), "actualizado": j.get("updatedAt"),
        "campos": [c.get("name") for g in j.get("fieldGroups", []) for c in g.get("fields", [])],
        "valor_programa": (oculto or {}).get("defaultValue") or (oculto or {}).get("defaultValues"),
    }
    print(f"{fid}: '{j.get('name')}' · archivado={j.get('archived')} · programa={res['formularios'][fid]['valor_programa']}")

print(hs.guardar("13_formularios_canon.json", res))
