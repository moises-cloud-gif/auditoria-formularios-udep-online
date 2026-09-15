#!/usr/bin/env python3
"""Ronda 1. Lee por API la definicion real de los 40 formularios."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

SUFIJO = "__udn_udep_"
res = {"generado": hs.ahora(), "formularios": {}, "errores": []}

for pag in hs.paginas():
    fid = pag.get("form_id_esperado")
    if not fid:
        res["errores"].append({"slug": pag["slug"], "motivo": "la pagina no declara un formId unico"})
        continue
    r = hs.api("GET", f"/marketing/v3/forms/{fid}")
    if r.status_code != 200:
        res["errores"].append({"slug": pag["slug"], "formId": fid,
                               "http": r.status_code, "cuerpo": r.text[:300]})
        continue
    j = r.json()
    campos = []
    for grupo in j.get("fieldGroups", []):
        for c in grupo.get("fields", []):
            campos.append({
                "nombre": c.get("name"), "etiqueta": c.get("label"),
                "tipo": c.get("fieldType"), "obligatorio": c.get("required"),
                "oculto": c.get("hidden"),
                "opciones": [o.get("value") for o in c.get("options", [])] or None,
            })
    texto = str(j)
    res["formularios"][fid] = {
        "slug": pag["slug"],
        "nombre": j.get("name"),
        "campos": campos,
        "cantidad_campos": len(campos),
        "sin_sufijo": [c["nombre"] for c in campos
                       if c["nombre"] in ("medio_de_contacto", "mensaje", "nivel_de_estudios")
                       and SUFIJO not in (c["nombre"] or "")],
        "tiene_clausula_datos": bool(j.get("legalConsentOptions", {}).get("type")) or "consentimiento" in texto.lower(),
        "mensaje_confirmacion": (j.get("configuration", {}) or {}).get("postSubmitAction", {}),
        "unidad_de_negocio": j.get("businessUnitId", "NO_EXPUESTO_POR_API"),
        "tipo_suscripcion": j.get("subscriptionTypeIds", "NO_EXPUESTO_POR_API"),
    }
    print(f"{pag['slug']}: {len(campos)} campos")

print(hs.guardar("11_formularios.json", res))
print(f"FORMULARIOS: {len(res['formularios'])}/40 · ERRORES: {len(res['errores'])}")
if any(e.get("http") == 403 for e in res["errores"]):
    print("BLOQUEANTE: la API devolvio 403. El inventario de esos formularios hay que hacerlo a mano.")
