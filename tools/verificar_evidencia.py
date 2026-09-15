#!/usr/bin/env python3
"""Ronda 4, parte programatica. No opina: cuenta.

El juez no puede dar PASA si este script falla. Es la defensa contra un loop
que corre rondas sin haber tocado HubSpot ni haber abierto una pagina.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

fallos = []


def exigir(cond, mensaje):
    if not cond:
        fallos.append(mensaje)
    print(f"{'ok  ' if cond else 'FALLA'} {mensaje}")


try:
    pre = hs.leer("00_preflight.json")
    exigir(pre.get("veredicto") == "PASA", "El preflight de accesos esta en PASA")
except FileNotFoundError:
    exigir(False, "Existe output/00_preflight.json")

# Regla: no se exige que TODO haya salido bien, se exige que todo lo que falto
# tenga un motivo registrado. Un 403 de la API es un hallazgo legitimo del proyecto,
# no puede dejar al loop sin forma de cerrar.
try:
    j = hs.leer("10_paginas.json")
    pgs = j["paginas"]
    ok = [p for p in pgs if not p.get("error")]
    exigir(len(pgs) == 40, f"Se intentaron las 40 paginas (se intentaron {len(pgs)})")
    exigir(all(p.get("error") for p in pgs if p not in ok),
           f"Toda pagina no recorrida tiene motivo registrado ({len(pgs)-len(ok)} sin recorrer)")
    exigir(len(ok) > 0, "Se recorrio al menos una pagina del sitio de verdad")
except FileNotFoundError:
    exigir(False, "Existe output/10_paginas.json")

try:
    j = hs.leer("11_formularios.json")
    forms, errores = j["formularios"], j.get("errores", [])
    exigir(len(forms) + len(errores) >= 40,
           f"Se intentaron los 40 formularios ({len(forms)} leidos + {len(errores)} con error)")
    exigir(all(e.get("http") or e.get("motivo") for e in errores),
           "Todo formulario no leido tiene codigo HTTP o motivo registrado")
    exigir(len(forms) > 0, "Se leyo al menos un formulario por API de verdad")
except FileNotFoundError:
    exigir(False, "Existe output/11_formularios.json")

try:
    act = hs.leer("12_activadores.json")
    exigir(act.get("flows_revisados", 0) > 0, "Se revisaron flows del portal")
except FileNotFoundError:
    exigir(False, "Existe output/12_activadores.json")

try:
    env = hs.leer("30_envios.json")
    inst = env["instancias"]
    exigir(len(inst) >= 80, f"Se intentaron las 80 instancias (hay {len(inst)})")
    sin_motivo = [i["slug"] + "/" + i.get("instancia", "?") for i in inst
                  if not i.get("R3_envio") and not i.get("error")]
    exigir(not sin_motivo,
           f"Toda instancia no enviada tiene motivo registrado ({len(sin_motivo)} sin el)")
    exigir(not all(i.get("dry_run") for i in inst),
           "Al menos una instancia se ejecuto de verdad (no todo en DRY_RUN)")

    correos = [i.get("correo") for i in inst if i.get("correo")]
    exigir(len(correos) == len(set(correos)), "Ningun correo de prueba esta repetido entre instancias")

    sin_captura = [i["slug"] + "/" + i.get("instancia", "?") for i in inst
                   if not i.get("captura") or not (hs.EVID / str(i.get("captura"))).exists()]
    exigir(not sin_captura, f"Toda instancia tiene captura en disco ({len(sin_captura)} sin ella)")

    enviadas = [i for i in inst if i.get("R3_envio")]
    con_id = [i for i in enviadas if i.get("hs_object_id")]
    exigir(len(enviadas) == 0 or len(con_id) == len(enviadas),
           f"Toda instancia enviada tiene hs_object_id real ({len(con_id)}/{len(enviadas)})")

    # Contraste duro: los contactos reportados tienen que existir en el portal.
    if con_id:
        muestra = con_id[: min(10, len(con_id))]
        vivos = 0
        for i in muestra:
            r = hs.api("GET", f"/crm/v3/objects/contacts/{i['hs_object_id']}")
            if r.status_code == 200:
                vivos += 1
        exigir(vivos == len(muestra),
               f"Los contactos reportados existen en el portal ({vivos}/{len(muestra)} de la muestra)")
except FileNotFoundError:
    exigir(False, "Existe output/30_envios.json")

print("\nVERIFICADOR PROGRAMATICO:", "PASA" if not fallos else "FALLA")
for f in fallos:
    print("  hueco:", f)
sys.exit(0 if not fallos else 1)
