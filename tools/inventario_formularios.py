#!/usr/bin/env python3
"""Ronda 1. Lee por API la definicion real de los 40 formularios.

Ademas de campos, guarda por formulario: valor por defecto de los campos ocultos
(es lo que atribuye el programa), bloques de texto enriquecido (encabezado),
clausula legal, configuracion (incluye reCAPTCHA) y la respuesta cruda completa
en output/evidencia/formularios/<formId>.json.
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

SUFIJO = "__udn_udep_"
# Propiedades propias de UDEP que DEBEN llevar sufijo. 'mensaje' no lleva sufijo en la
# plantilla de referencia (d6c333ed), asi que no se cuenta como error; lo que si es
# desvio es usar la propiedad generica de HubSpot 'message' en su lugar.
BASES_CON_SUFIJO = ("medio_de_contacto", "nivel_de_estudios", "cursos_piura", "programas_piura")

RAW = hs.EVID / "formularios"
RAW.mkdir(parents=True, exist_ok=True)

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
    (RAW / f"{fid}.json").write_text(json.dumps(j, ensure_ascii=False, indent=2), encoding="utf-8")

    campos, textos = [], []
    for grupo in j.get("fieldGroups", []):
        if grupo.get("richText"):
            textos.append({"tipo": grupo.get("richTextType"), "html": grupo.get("richText")})
        for c in grupo.get("fields", []):
            campos.append({
                "nombre": c.get("name"), "etiqueta": c.get("label"),
                "tipo": c.get("fieldType"), "obligatorio": c.get("required"),
                "oculto": c.get("hidden"),
                "valor_por_defecto": c.get("defaultValue") or c.get("defaultValues") or None,
                "opciones": [o.get("value") for o in c.get("options", [])] or None,
            })
    nombres = [c["nombre"] or "" for c in campos]
    sin_sufijo = [n for n in nombres if any(n == b for b in BASES_CON_SUFIJO)]
    oculto_programa = next((c for c in campos if c["oculto"] and
                            (c["nombre"] or "").startswith(("cursos_piura", "programas_piura"))), None)
    legal = j.get("legalConsentOptions") or {}
    conf = j.get("configuration") or {}
    res["formularios"][fid] = {
        "slug": pag["slug"],
        "nombre": j.get("name"),
        "tipo_formulario": j.get("formType"),
        "archivado": j.get("archived"),
        "creado": j.get("createdAt"), "actualizado": j.get("updatedAt"),
        "campos": campos,
        "cantidad_campos": len(campos),
        "textos_enriquecidos": textos,
        "tiene_encabezado": any("INFORMACI" in (t["html"] or "").upper() for t in textos),
        "sin_sufijo": sin_sufijo,
        "usa_message_generico": "message" in nombres,
        "campo_oculto_programa": oculto_programa["nombre"] if oculto_programa else None,
        "valor_programa": oculto_programa["valor_por_defecto"] if oculto_programa else None,
        "tiene_clausula_datos": bool(legal.get("type")) and legal.get("type") != "none",
        "clausula_datos": legal,
        "mensaje_confirmacion": conf.get("postSubmitAction", {}),
        "recaptcha_habilitado": conf.get("recaptchaEnabled", "NO_EXPUESTO_POR_API"),
        "configuracion": conf,
        "unidad_de_negocio": j.get("businessUnitId", "NO_EXPUESTO_POR_API"),
        "tipo_suscripcion": j.get("subscriptionTypeIds", "NO_EXPUESTO_POR_API"),
    }
    print(f"{pag['slug']}: {len(campos)} campos · programa={res['formularios'][fid]['valor_programa']}")

print(hs.guardar("11_formularios.json", res))
print(f"FORMULARIOS: {len(res['formularios'])}/40 · ERRORES: {len(res['errores'])}")
if any(e.get("http") == 403 for e in res["errores"]):
    print("BLOQUEANTE: la API devolvio 403. El inventario de esos formularios hay que hacerlo a mano.")
