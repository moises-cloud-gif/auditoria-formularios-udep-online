#!/usr/bin/env python3
"""Genera output/registro_pruebas.csv: una fila por instancia (banner y modal) de cada pagina.

Cruza la matriz de la ronda 2 (20_matriz.json) con los envios de la ronda 3 (30_envios.json)
si existen. Mientras la ronda 3 no haya corrido, R1..R5, H1, H2 y H5 quedan en PENDIENTE y la
columna ronda3_ejecutada dice NO. Este script no consulta HubSpot: solo consolida evidencia.
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

COLS = ["pagina", "url", "instancia", "form_id_esperado", "form_id_en_pagina", "form_id_registrado",
        "fecha_hora", "correo_prueba", "ronda3_ejecutada",
        "R1_renderiza", "R2_campos", "R3_envio", "R4_confirmacion", "R5_clausula_datos",
        "H1_contacto", "H2_atribucion", "H3_programa", "H4_activador", "H5_disparo", "H6_marca", "H7_definicion",
        "caso", "severidad", "accion", "quien", "observacion"]

def sn(v):
    return "SI" if v is True else ("NO" if v is False else ("PENDIENTE" if v is None else str(v)))

filas = []
for pag in hs.paginas():
    m = matriz[pag["slug"]]
    for inst in ("banner", "modal"):
        e = envios.get((pag["slug"], inst))
        h7 = [h["detalle"] for h in m["hallazgos"] if h["check"] == "H7"]
        obs = "; ".join(h["detalle"] for h in m["hallazgos"] if h["check"] not in ("H7",))
        fila = {
            "pagina": pag["slug"], "url": pag["url"], "instancia": inst,
            "form_id_esperado": pag["form_id_esperado"],
            "form_id_en_pagina": ",".join(m.get("form_id_en_pagina") or []),
            "form_id_registrado": (e or {}).get("form_id_registrado", "PENDIENTE"),
            "fecha_hora": (e or {}).get("fecha", ""),
            "correo_prueba": (e or {}).get("correo", ""),
            "ronda3_ejecutada": "SI" if e and not e.get("dry_run") else "NO",
            "R1_renderiza": sn((e or {}).get("R1_renderiza")),
            "R2_campos": sn(bool((e or {}).get("R2_campos")) if e else None),
            "R3_envio": sn((e or {}).get("R3_envio")),
            "R4_confirmacion": sn((e or {}).get("R4_confirmacion")),
            "R5_clausula_datos": sn((e or {}).get("R5_clausula_datos")),
            "H1_contacto": sn((e or {}).get("H1_contacto")),
            "H2_atribucion": sn((e or {}).get("H2_atribucion")),
            "H3_programa": m["H3"] or "PENDIENTE",
            "H4_activador": m["H4"],
            "H5_disparo": sn((e or {}).get("H5_disparo")),
            "H6_marca": m["H6"],
            "H7_definicion": "OK" if not h7 else " | ".join(h7),
            "caso": m["caso"], "severidad": m["severidad_max"] or "",
            "accion": m["accion"], "quien": m["quien"] or "",
            "observacion": obs + (f"; error ronda 3: {e['error']}" if e and e.get("error") else ""),
        }
        filas.append(fila)

destino = hs.OUT / "registro_pruebas.csv"
with destino.open("w", newline="", encoding="utf-8-sig") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    w.writerows(filas)
print(f"output/registro_pruebas.csv · {len(filas)} filas · con ronda 3: {sum(1 for f in filas if f['ronda3_ejecutada']=='SI')}")
