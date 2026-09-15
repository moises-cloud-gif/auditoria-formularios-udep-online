#!/usr/bin/env python3
"""Limpieza de los contactos de prueba. Arranca en seco y exige aprobacion humana.

Uso:
  python3 tools/limpiar_pruebas.py                 # lista lo que borraria
  python3 tools/limpiar_pruebas.py --ejecutar      # borra (pasa por 'ask' en settings)
"""
import sys, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

ap = argparse.ArgumentParser()
ap.add_argument("--ejecutar", action="store_true")
a = ap.parse_args()

usuario, dominio = hs.QA_BASE.split("@", 1)
patron = f"{usuario}+"

r = hs.api("POST", "/crm/v3/objects/contacts/search", json={
    "filterGroups": [{"filters": [
        {"propertyName": "email", "operator": "CONTAINS_TOKEN", "value": f"{patron}*"}]}],
    "properties": ["email", "createdate"], "limit": 100})

if r.status_code != 200:
    print(f"ERROR HTTP {r.status_code}: {r.text[:200]}")
    sys.exit(1)

encontrados = r.json().get("results", [])
print(f"Contactos de prueba encontrados: {len(encontrados)}")
for c in encontrados[:20]:
    print("  ", c["id"], c["properties"].get("email"))

if not a.ejecutar:
    print("\nModo seco. Nada se borro. Para borrar de verdad: --ejecutar")
    sys.exit(0)

ids = [{"id": c["id"]} for c in encontrados]
for i in range(0, len(ids), 100):
    rr = hs.api("POST", "/crm/v3/objects/contacts/batch/archive", json={"inputs": ids[i:i + 100]})
    print(f"lote {i//100 + 1}: HTTP {rr.status_code}")
print("Limpieza terminada. Verificar corriendo el script otra vez en modo seco.")
