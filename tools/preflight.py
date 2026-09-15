#!/usr/bin/env python3
"""Ronda 0. Seis comprobaciones de acceso con evidencia en disco.

Si esto no pasa, ninguna ronda posterior tiene sentido: el agente estaria
produciendo texto sobre un sistema que no puede ver.
"""
import json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

FORM_REFERENCIA = "d6c333ed-17db-4e16-8afa-d87ef1b4eb49"  # Curso Gestion del Talento Piura

res = {"generado": hs.ahora(), "dry_run": hs.DRY_RUN, "checks": {}}


def check(nombre, fn):
    try:
        ok, detalle = fn()
    except Exception as e:
        ok, detalle = False, f"{type(e).__name__}: {e}"
    res["checks"][nombre] = {"pasa": ok, "detalle": detalle}
    print(f"{'PASA ' if ok else 'FALLA'} {nombre}: {detalle}")
    return ok


def p1():
    hs.guarda_portal()
    return True, f"token valido sobre el portal {hs.PORTAL}"


def p2():
    r = hs.api("GET", f"/marketing/v3/forms/{FORM_REFERENCIA}")
    if r.status_code != 200:
        return False, f"HTTP {r.status_code} — {r.text[:200]}"
    j = r.json()
    campos = sum(len(g.get("fields", [])) for g in j.get("fieldGroups", []))
    return True, f"formulario de referencia '{j.get('name')}' con {campos} campos"


def p3():
    r = hs.api("GET", "/crm/v3/objects/contacts?limit=1")
    if r.status_code != 200:
        return False, f"HTTP {r.status_code} — {r.text[:200]}"
    return True, "scope de lectura de contactos activo"


def p4():
    r = hs.api("GET", "/automation/v4/flows?limit=1")
    if r.status_code != 200:
        return False, f"HTTP {r.status_code} — {r.text[:200]}"
    return True, "scope de automation activo"


def p5():
    from playwright.sync_api import sync_playwright
    pag = hs.paginas()[0]
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        pg = b.new_page()
        pg.goto(pag["url"], timeout=60000, wait_until="networkidle")
        pg.wait_for_timeout(4000)
        inputs = pg.locator("form input").count()
        destino = hs.EVID / "preflight_render.png"
        pg.screenshot(path=str(destino), full_page=False)
        b.close()
    if inputs == 0:
        return False, f"Playwright abrio {pag['slug']} pero no renderizo ningun campo"
    return True, f"{inputs} campos renderizados en {pag['slug']}, captura en {destino.name}"


def p6():
    import requests
    malas = []
    for pag in hs.paginas():
        try:
            c = requests.head(pag["url"], timeout=20, allow_redirects=True).status_code
        except Exception as e:
            c = str(e)[:40]
        if c != 200:
            malas.append({"slug": pag["slug"], "http": c})
    if malas:
        return False, f"{len(malas)} de 40 paginas no responden 200: {malas[:5]}"
    return True, "las 40 paginas responden 200"


todos = all([check("P1_token_y_portal", p1), check("P2_scope_forms", p2),
             check("P3_scope_contacts", p3), check("P4_scope_automation", p4),
             check("P5_playwright_render", p5), check("P6_paginas_vivas", p6)])

res["veredicto"] = "PASA" if todos else "FALLA"
print("\n" + hs.guardar("00_preflight.json", res))
print(f"VEREDICTO: {res['veredicto']}")
sys.exit(0 if todos else 1)
