#!/usr/bin/env python3
"""Comprobacion rapida y de solo lectura: los 6 Activadores conocidos siguen referenciando
los 40 formularios de UDEP? Compara contra la foto de output/12_activadores.json.

Sirve para detectar si alguien modifico los workflows despues del inventario.
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

foto = hs.leer("12_activadores.json")
flows = foto["flows_con_formularios_udep"]
fids = {p["form_id_esperado"]: p["slug"] for p in hs.paginas() if p.get("form_id_esperado")}

print(f"Foto del inventario: {foto['generado']}")
print(f"Comprobando {len(flows)} Activadores ahora mismo\n")
antes_total = ahora_total = 0
cambios = []
for fid_flow, info in flows.items():
    r = hs.api("GET", f"/automation/v4/flows/{fid_flow}")
    if r.status_code != 200:
        print(f"{fid_flow} · {info['nombre'][:55]} -> HTTP {r.status_code}")
        cambios.append((info["nombre"], f"no se pudo leer: HTTP {r.status_code}"))
        continue
    j = r.json()
    crudo = json.dumps(j)
    ahora = [f for f in fids if f in crudo]
    antes = info["form_ids_referenciados"]
    antes_total += len(antes); ahora_total += len(ahora)
    quitados = [f for f in antes if f not in ahora]
    agregados = [f for f in ahora if f not in antes]
    estado = "SIN CAMBIOS" if not quitados and not agregados else "CAMBIO"
    print(f"{estado:12} {info['nombre'][:58]:58} antes {len(antes):2} · ahora {len(ahora):2} · activo: {j.get('isEnabled')}")
    if j.get("isEnabled") != info.get("activo"):
        cambios.append((info["nombre"], f"estado activo cambio: {info.get('activo')} -> {j.get('isEnabled')}"))
        print(f"             !! el flujo paso de activo={info.get('activo')} a activo={j.get('isEnabled')}")
    for f in quitados:
        cambios.append((info["nombre"], f"quitaron el formulario de {fids[f]} ({f[:8]})"))
        print(f"             - quitado: {fids[f]} ({f[:8]})")
    for f in agregados:
        cambios.append((info["nombre"], f"agregaron el formulario de {fids[f]} ({f[:8]})"))
        print(f"             + agregado: {fids[f]} ({f[:8]})")

print(f"\nReferencias a formularios de UDEP · antes: {antes_total} · ahora: {ahora_total}")
print("VEREDICTO:", "SIN CAMBIOS en los Activadores" if not cambios else f"HAY {len(cambios)} CAMBIO(S)")
hs.guardar("43_estado_activadores.json", {"generado": hs.ahora(), "foto_original": foto["generado"],
                                          "referencias_antes": antes_total, "referencias_ahora": ahora_total,
                                          "cambios": cambios})
