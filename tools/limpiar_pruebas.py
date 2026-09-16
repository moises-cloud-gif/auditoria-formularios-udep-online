#!/usr/bin/env python3
"""Limpieza de los contactos de prueba. Arranca en seco y exige aprobacion humana.

Uso:
  python3 tools/limpiar_pruebas.py                 # lista lo que borraria
  python3 tools/limpiar_pruebas.py --ejecutar      # borra (pasa por 'ask' en settings)

Guarda de seguridad (16-sep-2026): la busqueda de HubSpot por "qa+*" tambien devuelve contactos
reales cuyo correo contiene "_qa" (por ejemplo leads de Facebook de UANDES). Por eso, ademas de la
busqueda, cada correo tiene que cumplir EXACTAMENTE el patron de la prueba
  qa+<slug>-<banner|modal>-<AAAAMMDD>@5minutos.io
Lo que no cumpla se lista como EXCLUIDO y no se toca jamas.
"""
import sys, pathlib, argparse, re
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

ap = argparse.ArgumentParser()
ap.add_argument("--ejecutar", action="store_true")
a = ap.parse_args()

usuario, dominio = hs.QA_BASE.split("@", 1)
PATRON = re.compile(rf"^{re.escape(usuario)}\+[a-z0-9-]+-(banner|modal)-\d{{8}}@{re.escape(dominio)}$", re.I)

encontrados, after = [], None
while True:
    cuerpo = {"filterGroups": [{"filters": [
        {"propertyName": "email", "operator": "CONTAINS_TOKEN", "value": f"{usuario}+*"}]}],
        "properties": ["email", "createdate", "firstname", "lastname"], "limit": 100}
    if after:
        cuerpo["after"] = after
    r = hs.api("POST", "/crm/v3/objects/contacts/search", json=cuerpo)
    if r.status_code != 200:
        print(f"ERROR HTTP {r.status_code}: {r.text[:200]}")
        sys.exit(1)
    j = r.json()
    encontrados += j.get("results", [])
    after = (j.get("paging", {}).get("next", {}) or {}).get("after")
    if not after:
        break

de_prueba = [c for c in encontrados if PATRON.match((c["properties"].get("email") or "").strip())]
excluidos = [c for c in encontrados if c not in de_prueba]

print(f"Contactos que devuelve la busqueda: {len(encontrados)}")
print(f"  Cumplen el patron de prueba y SE BORRARIAN: {len(de_prueba)}")
for c in de_prueba[:100]:
    print("     ", c["id"], c["properties"].get("email"), (c["properties"].get("createdate") or "")[:10])
print(f"  EXCLUIDOS (no cumplen el patron, no se tocan): {len(excluidos)}")
for c in excluidos[:20]:
    print("     ", c["id"], c["properties"].get("email"), (c["properties"].get("createdate") or "")[:10])

hs.guardar("90_limpieza.json", {"generado": hs.ahora(), "modo": "ejecutar" if a.ejecutar else "seco",
            "a_borrar": [{"id": c["id"], "email": c["properties"].get("email")} for c in de_prueba],
            "excluidos": [{"id": c["id"], "email": c["properties"].get("email")} for c in excluidos]})

if not a.ejecutar:
    print("\nModo seco. Nada se borro. Para borrar de verdad: --ejecutar")
    sys.exit(0)

if not de_prueba:
    print("\nNo hay contactos de prueba para borrar.")
    sys.exit(0)

ids = [{"id": c["id"]} for c in de_prueba]
for i in range(0, len(ids), 100):
    rr = hs.api("POST", "/crm/v3/objects/contacts/batch/archive", json={"inputs": ids[i:i + 100]})
    print(f"lote {i//100 + 1}: HTTP {rr.status_code}")
print("Limpieza terminada. Verificar corriendo el script otra vez en modo seco.")
