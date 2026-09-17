#!/usr/bin/env python3
"""Resumen legible de lo que quedo registrado en output/30_envios.json.

Uso:  python tools/ver_tanda.py
Sirve despues de cada tanda, en seco o en la pasada real.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

try:
    d = hs.leer("30_envios.json")
except FileNotFoundError:
    print("Todavia no hay output/30_envios.json. Corre primero tools/probar_envios.py")
    sys.exit(0)

inst = d["instancias"]
print(f"Instancias registradas: {len(inst)}/80 · modo seco en el archivo: {d.get('dry_run')}")
print()
print(f"{'pagina':45} {'inst':7} {'R1':5} {'R3':5} {'R4':5} {'R5':5} {'campos':6} {'captcha prueba':14} formulario")
print("-" * 125)
for i in inst:
    print(f"{i['slug'][:45]:45} {i.get('instancia',''):7} "
          f"{str(i.get('R1_renderiza')):5} {str(i.get('R3_envio')):5} "
          f"{str(i.get('R4_confirmacion')):5} {str(i.get('R5_clausula_datos')):5} "
          f"{len(i.get('R2_campos') or []):6} {str(i.get('recaptcha_clave_de_prueba')):14} "
          f"{(i.get('form_id_disparado') or '')[:8]}")
    if i.get("campos_no_llenados"):
        print(f"      NO se pudo llenar: {', '.join(i['campos_no_llenados'])}")
    if i.get("errores_de_validacion"):
        print(f"      el formulario rechazo: {' | '.join(i['errores_de_validacion'])[:120]}")
    if i.get("error") and "DRY_RUN" not in str(i.get("error")):
        print(f"      error: {i['error'][:110]}")

def cuenta(k):
    return sum(1 for i in inst if i.get(k))

print()
print(f"Renderizaron (R1): {cuenta('R1_renderiza')}/{len(inst)}")
print(f"Enviaron (R3): {cuenta('R3_envio')}/{len(inst)}")
print(f"Mensaje de confirmacion (R4): {cuenta('R4_confirmacion')}/{len(inst)}")
print(f"Clausula de datos visible (R5): {cuenta('R5_clausula_datos')}/{len(inst)}")
print(f"Con aviso de reCAPTCHA de prueba: {cuenta('recaptcha_clave_de_prueba')}/{len(inst)}")
print(f"Contacto creado en HubSpot (H1): {cuenta('H1_contacto')}/{len(inst)}")
faltan = [f"{i['slug']}/{i.get('instancia')}" for i in inst
          if not i.get("captura") or not (hs.EVID / str(i.get("captura"))).exists()]
print(f"Sin captura en disco: {len(faltan)} {faltan[:5] if faltan else ''}")
