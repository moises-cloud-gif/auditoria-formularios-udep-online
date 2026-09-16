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
    """El sitio usa el embed v2 de HubSpot: el formulario vive DENTRO de un iframe.
    Contar 'form input' en la pagina principal siempre da cero. Se cuenta en los marcos."""
    import os
    from playwright.sync_api import sync_playwright
    pag = hs.paginas()[0]
    visible = os.getenv("PW_VISIBLE", "0") == "1"
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=not visible)
        ctx = b.new_context(viewport={"width": 1440, "height": 900}, locale="es-PE")
        pg = ctx.new_page()
        pg.goto(pag["url"], timeout=90000, wait_until="domcontentloaded")
        pg.wait_for_timeout(9000)
        en_pagina = pg.locator("form input").count()
        en_marcos = sum(f.locator("input, select, textarea").count() for f in pg.frames[1:])
        iframes = pg.locator("iframe.hs-form-iframe, iframe[id^='hs-form-iframe']").count()
        titulo = pg.title()
        destino = hs.EVID / "preflight_render.png"
        pg.screenshot(path=str(destino), full_page=False)
        b.close()
    if "just a moment" in titulo.lower():
        return False, "Cloudflare esta desafiando al navegador. Reintenta con PW_VISIBLE=1"
    total = en_pagina + en_marcos
    if total == 0:
        return False, (f"Playwright abrio {pag['slug']} pero no renderizo ningun campo "
                       f"(iframes de formulario detectados: {iframes})")
    return True, (f"{total} campos renderizados en {pag['slug']} "
                  f"({en_marcos} dentro del iframe de HubSpot), captura en {destino.name}")


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
