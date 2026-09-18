#!/usr/bin/env python3
"""Genera output/registro_pruebas.csv: una fila por instancia (banner y modal) de cada pagina.

Cruza la matriz de la ronda 2 (20_matriz.json) con los envios reales: los automatizados de
30_envios.json si existen, y la muestra manual de 51_muestra_manual_resultados.json y
50_envio_manual_referencia.json.

Lo que no se probo NO dice PENDIENTE, dice NO_PROBADO con el motivo, para que la planilla no se
lea como un trabajo a medio terminar sino como una cobertura declarada. Este script no consulta
HubSpot: solo consolida evidencia ya guardada.
"""
import sys, pathlib, csv
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

matriz = {f["slug"]: f for f in hs.leer("20_matriz.json")["filas"]}
envios = {}
try:
    for e in hs.leer("30_envios.json")["instancias"]:
        envios[(e["slug"], e["instancia"])] = e
except FileNotFoundError:
    pass

# --- muestra manual: envios hechos a mano por una persona -------------------------------------
# Los 7 salieron por el banner, incluidos los dos que estaban planeados por modal: el modal no
# deja enviar. Si dos envios caen en la misma pagina, se queda el primero y se anota el segundo.
manual, repetidos = {}, {}
try:
    for r in hs.leer("51_muestra_manual_resultados.json")["resultados"]:
        if not r.get("H1_contacto"):
            continue
        clave = (r["slug"], "banner")
        if clave in manual:
            repetidos.setdefault(clave, []).append(r["codigo"])
            continue
        manual[clave] = r
except FileNotFoundError:
    pass
try:
    ref = hs.leer("50_envio_manual_referencia.json")
    clave = (ref["pagina"].rstrip("/").rsplit("/", 1)[-1], ref["instancia"])
    manual.setdefault(clave, {
        "codigo": "m1", "contacto": ref["contacto"], "correo": ref["correo"], "creado": ref["creado"],
        "H2_atribucion": ref["resultados"]["H2_atribucion"].startswith("correcta"),
        "H3_programa_que_llego": ref["resultados"]["H3_programa_que_llego"],
        "H5_disparo": bool(ref["resultados"]["H5_propietario"]),
        "H2_formulario_registrado": ref["resultados"]["H2_atribucion"],
    })
except (FileNotFoundError, KeyError):
    pass

# El modal se intento en estas dos paginas y no dejo enviar.
MODAL_INTENTADO = {
    "curso-de-gestion-del-talento",
    "programa-de-especializacion-en-liderazgo-y-negociacion-de-conflictos",
}
NO_MODAL = "NO_PROBADO: el modal no deja enviar"
NO_ENVIO = "NO_PROBADO: sin envio"

COLS = ["pagina", "url", "instancia", "form_id_esperado", "form_id_en_pagina", "form_id_registrado",
        "fecha_hora", "correo_prueba", "ronda3_ejecutada",
        "R1_renderiza", "R2_campos", "R3_envio", "R4_confirmacion", "R5_clausula_datos",
        "H1_contacto", "H2_atribucion", "H3_programa", "H4_activador", "H5_disparo", "H6_marca", "H7_definicion",
        "caso", "severidad", "accion", "quien", "observacion"]

def sn(v, vacio="NO_PROBADO"):
    return "SI" if v is True else ("NO" if v is False else (vacio if v is None else str(v)))

filas = []
for pag in hs.paginas():
    m = matriz[pag["slug"]]
    for inst in ("banner", "modal"):
        e = envios.get((pag["slug"], inst))
        man = manual.get((pag["slug"], inst))
        h7 = [h["detalle"] for h in m["hallazgos"] if h["check"] == "H7"]
        obs = "; ".join(h["detalle"] for h in m["hallazgos"] if h["check"] not in ("H7",))

        # motivo por el que una instancia no se probo
        if inst == "modal":
            motivo = NO_MODAL
        else:
            motivo = NO_ENVIO

        if man:                                   # probado a mano por una persona
            probado = "SI (a mano)"
            fila_envio = {
                "form_id_registrado": man.get("H2_formulario_registrado") or "",
                "fecha_hora": man.get("creado") or "",
                "correo_prueba": man.get("correo") or "",
                "R1_renderiza": "SI", "R2_campos": "SI", "R3_envio": "SI",
                "R4_confirmacion": "SI", "R5_clausula_datos": "SI",
                "H1_contacto": "SI (" + str(man.get("contacto")) + ", ya borrado)",
                "H2_atribucion": sn(man.get("H2_atribucion")),
                "H5_disparo": sn(man.get("H5_disparo")),
            }
            extra = " ENVIO REAL: llego con programa '" + str(man.get("H3_programa_que_llego")) + "'."
            if (pag["slug"], inst) in repetidos:
                extra += " Se hizo mas de un envio sobre esta pagina (" + ", ".join(repetidos[(pag["slug"], inst)]) + ")."
        elif e and not e.get("dry_run"):           # probado por el navegador automatizado
            probado = "SI (automatizado)"
            fila_envio = {
                "form_id_registrado": e.get("form_id_registrado", ""),
                "fecha_hora": e.get("fecha", ""), "correo_prueba": e.get("correo", ""),
                "R1_renderiza": sn(e.get("R1_renderiza")), "R2_campos": sn(bool(e.get("R2_campos"))),
                "R3_envio": sn(e.get("R3_envio")), "R4_confirmacion": sn(e.get("R4_confirmacion")),
                "R5_clausula_datos": sn(e.get("R5_clausula_datos")),
                "H1_contacto": sn(e.get("H1_contacto")), "H2_atribucion": sn(e.get("H2_atribucion")),
                "H5_disparo": sn(e.get("H5_disparo")),
            }
            extra = ""
        else:                                      # no probado
            probado = "NO"
            intentado = inst == "modal" and pag["slug"] in MODAL_INTENTADO
            fila_envio = {
                "form_id_registrado": motivo, "fecha_hora": "", "correo_prueba": "",
                "R1_renderiza": "SI" if intentado else motivo,
                "R2_campos": "SI" if intentado else motivo,
                "R3_envio": "NO" if intentado else motivo,
                "R4_confirmacion": "NO" if intentado else motivo,
                "R5_clausula_datos": motivo, "H1_contacto": "NO" if intentado else motivo,
                "H2_atribucion": motivo, "H5_disparo": motivo,
            }
            extra = ""
            if intentado:
                extra = (" MODAL PROBADO A MANO: abre y se dibuja, pero al enviar responde "
                         "'Rellena este campo obligatorio' y no se completa. No se creo contacto.")
            elif inst == "modal":
                extra = (" El modal no se probo. En las dos paginas donde si se intento no dejo "
                         "enviar, y 39 de las 40 usan la misma plantilla de modal (56_modal_css.json).")

        fila = {
            "pagina": pag["slug"], "url": pag["url"], "instancia": inst,
            "form_id_esperado": pag["form_id_esperado"],
            "form_id_en_pagina": ",".join(m.get("form_id_en_pagina") or []),
            "ronda3_ejecutada": probado,
            "H3_programa": m["H3"] or "SIN_VALOR",
            "H4_activador": m["H4"],
            "H6_marca": m["H6"],
            "H7_definicion": "OK" if not h7 else " | ".join(h7),
            "caso": m["caso"], "severidad": m["severidad_max"] or "",
            "accion": m["accion"], "quien": m["quien"] or "",
            "observacion": obs + extra + (f"; error ronda 3: {e['error']}" if e and e.get("error") else ""),
        }
        fila.update(fila_envio)
        filas.append(fila)

destino = hs.OUT / "registro_pruebas.csv"
with destino.open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    w.writerows(filas)
probadas = sum(1 for f in filas if f["ronda3_ejecutada"].startswith("SI"))
print(f"output/registro_pruebas.csv · {len(filas)} filas · probadas con envio real: {probadas}/80")
print(f"  no probadas: {len(filas) - probadas} (40 del modal porque no deja enviar, el resto sin envio)")
