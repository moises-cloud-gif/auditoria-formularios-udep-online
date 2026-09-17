#!/usr/bin/env python3
"""Solo lectura. Recorre todos los flows del portal y busca cuales escriben o filtran
propiedades que contengan 'mql'. Responde: donde se marca MQL un contacto, y si la cadena
de Activadores de UDEP esta involucrada. Sale output/46_donde_se_marca_mql.json.
"""
import sys, pathlib, json, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

CADENA = {"1631969831", "1631981721", "1631988744", "1631988748", "1645743473", "1854523916",
          "1631981736", "1631990199", "1631989399", "1741893789"}
res = {"generado": hs.ahora(), "flows_revisados": 0, "escriben_mql": [], "filtran_mql": []}
after = None
while True:
    ruta = "/automation/v4/flows?limit=100" + (f"&after={after}" if after else "")
    r = hs.api("GET", ruta)
    if r.status_code != 200:
        print("ERROR listando flows:", r.status_code); break
    j = r.json()
    for f in j.get("results", []):
        res["flows_revisados"] += 1
        det = hs.api("GET", f"/automation/v4/flows/{f['id']}")
        if det.status_code != 200:
            continue
        dj = det.json(); s = json.dumps(dj, ensure_ascii=False)
        if not re.search(r"mql", s, re.I):
            continue
        escribe = sorted({p for p in re.findall(r'"property_name":\s*"([^"]+)"', s) if "mql" in p.lower()})
        filtra = sorted({p for p in re.findall(r'"property"\s*:\s*"([^"]+)"', s) if "mql" in p.lower()})
        fila = {"flowId": str(f["id"]), "nombre": dj.get("name"), "activo": dj.get("isEnabled"),
                "escribe": escribe, "filtra": filtra, "en_la_cadena_udep": str(f["id"]) in CADENA}
        if escribe:
            res["escriben_mql"].append(fila)
            print(f"ESCRIBE  {f['id']} · {str(dj.get('name'))[:60]} · {escribe} · activo={dj.get('isEnabled')}")
        elif filtra:
            res["filtran_mql"].append(fila)
    after = (j.get("paging", {}).get("next", {}) or {}).get("after")
    if not after:
        break
print(hs.guardar("46_donde_se_marca_mql.json", res))
print(f"FLOWS REVISADOS: {res['flows_revisados']} · escriben MQL: {len(res['escriben_mql'])} · filtran MQL: {len(res['filtran_mql'])}")
print("En la cadena de UDEP:", [f["nombre"] for f in res["escriben_mql"] if f["en_la_cadena_udep"]] or "ninguno")
