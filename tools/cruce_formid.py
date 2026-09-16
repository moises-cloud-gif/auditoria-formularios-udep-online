#!/usr/bin/env python3
"""Cruce pagina por pagina: formId incrustado (banner y modal) vs. lo que HubSpot dice que es
ese formulario vs. lo que deberia ir en la pagina.

No consulta nada: consolida output/10_paginas.json (marcado vivo del sitio),
output/11_formularios.json (respuesta de la API de formularios) y output/20_matriz.json
(programa esperado por pagina). Sale output/cruce_formid_paginas.csv, una fila por pagina.
"""
import sys, pathlib, csv
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

pgs = {p["slug"]: p for p in hs.leer("10_paginas.json")["paginas"]}
forms = hs.leer("11_formularios.json")["formularios"]
matriz = {f["slug"]: f for f in hs.leer("20_matriz.json")["filas"]}

COLS = ["pagina", "url", "tipo",
        "formId_banner", "formId_modal", "incrustaciones_en_html",
        "formId_esperado_inventario_15sep", "banner_coincide", "modal_coincide",
        "nombre_formulario_segun_hubspot", "formulario_corresponde_a_la_pagina",
        "programa_que_envia_el_formulario", "programa_que_deberia_enviar", "programa_coincide",
        "activador_segun_hubspot",
        "formId_que_debe_ir_en_la_pagina", "vicente_debe_repuntar", "accion", "observacion"]

filas = []
for pag in hs.paginas():
    slug = pag["slug"]
    w = pgs[slug]
    m = matriz[slug]
    esperado = pag["form_id_esperado"]
    # En la pagina con 8 incrustaciones el modal real es la ultima con formId; las otras seis
    # tienen marcadores sin resolver.
    modal_ids = [i["formId"] for i in w["instancias"] if i["destino"] != "inline" and i["formId"]]
    modal = modal_ids[-1] if modal_ids else None
    banner = w.get("banner")
    f = forms.get(banner or esperado, {})
    nombre = f.get("nombre")
    activ = "; ".join(a["nombre"] for a in m["activadores"]) or "NINGUNO"
    obs = []
    if w.get("anomalia"):
        obs.append(f"marcado: {w['anomalia']} (6 bloques con HS_FORM_ID sin resolver)")
    if m["H3"] != "OK":
        obs.append({"OTRO_PROGRAMA": "el campo oculto envia otro programa",
                    "SIN_VALOR": "el campo oculto no tiene valor",
                    "SIN_OPCION": "no existe opcion para este programa en la propiedad"}.get(m["H3"], m["H3"]))
    if m["estado_activador"] == "SIN_ACTIVADOR":
        obs.append("sin Activador: el lead no se asigna")
    elif m["H4"] == "REVISAR":
        obs.append("revisar cluster del Activador")
    filas.append({
        "pagina": slug, "url": pag["url"], "tipo": pag["tipo"],
        "formId_banner": banner, "formId_modal": modal,
        "incrustaciones_en_html": w.get("llamadas_create"),
        "formId_esperado_inventario_15sep": esperado,
        "banner_coincide": "SI" if banner == esperado else "NO",
        "modal_coincide": "SI" if modal == esperado else "NO",
        "nombre_formulario_segun_hubspot": nombre,
        "formulario_corresponde_a_la_pagina": "SI" if m["caso"] in ("A", "B") else "NO",
        "programa_que_envia_el_formulario": m["programa_enviado"] or "",
        "programa_que_deberia_enviar": m["programa_esperado"] or "NO EXISTE OPCION",
        "programa_coincide": "SI" if m["H3"] == "OK" else "NO",
        "activador_segun_hubspot": activ,
        "formId_que_debe_ir_en_la_pagina": esperado,
        "vicente_debe_repuntar": "NO",
        "accion": m["accion"],
        "observacion": "; ".join(obs),
    })

destino = hs.OUT / "cruce_formid_paginas.csv"
with destino.open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader(); w.writerows(filas)
print(f"output/cruce_formid_paginas.csv · {len(filas)} filas")
print("banner coincide:", sum(f['banner_coincide']=='SI' for f in filas), "/ modal coincide:", sum(f['modal_coincide']=='SI' for f in filas))
print("formulario corresponde a la pagina:", sum(f['formulario_corresponde_a_la_pagina']=='SI' for f in filas))
print("programa coincide:", sum(f['programa_coincide']=='SI' for f in filas))
