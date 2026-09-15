#!/usr/bin/env python3
"""Ronda 3. Envio real con Playwright sobre banner y modal, y verificacion en HubSpot.

Uso:  python3 tools/probar_envios.py --desde 0 --hasta 10
Con DRY_RUN=1 recorre y captura pantalla pero NO envia. Eso no cierra la ronda.
"""
import sys, pathlib, argparse, datetime, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--desde", type=int, default=0)
ap.add_argument("--hasta", type=int, default=40)
a = ap.parse_args()

HOY = datetime.date.today().strftime("%Y%m%d")
paginas = hs.paginas()[a.desde:a.hasta]
filas = []


def completar_y_enviar(pg, raiz, slug, instancia):
    """Llena los campos visibles del formulario y envia. Devuelve el resultado por instancia."""
    correo = hs.correo_qa(slug, instancia, HOY)
    fila = {"slug": slug, "instancia": instancia, "correo": correo,
            "fecha": hs.ahora(), "dry_run": hs.DRY_RUN,
            "R1_renderiza": False, "R2_campos": [], "R3_envio": False,
            "R4_confirmacion": False, "R5_clausula_datos": False,
            "captura": None, "error": None}
    try:
        form = raiz.locator("form").first
        form.wait_for(state="visible", timeout=20000)
        fila["R1_renderiza"] = True
        fila["R2_campos"] = raiz.locator("form input, form select, form textarea").evaluate_all(
            "els => els.map(e => e.name || e.id).filter(Boolean)")
        fila["R5_clausula_datos"] = "autoriz" in raiz.inner_text().lower() or "datos personales" in raiz.inner_text().lower()

        def llenar(sel, val):
            loc = raiz.locator(sel).first
            if loc.count():
                loc.fill(val)

        llenar("input[name='firstname']", "QA")
        llenar("input[name='lastname']", f"Prueba {slug[:40]}")
        llenar("input[name='email']", correo)
        llenar("input[name='phone']", hs.QA_TEL)
        for sel in ("textarea[name='mensaje']", "textarea[name='mensaje__udn_udep_']"):
            llenar(sel, f"PRUEBA QA 5MINUTOS - {HOY} - NO GESTIONAR")
        for sel in ("select[name^='nivel_de_estudios']", "select[name^='medio_de_contacto']"):
            s = raiz.locator(sel).first
            if s.count():
                ops = s.locator("option").all_values() if hasattr(s, "all_values") else None
                try:
                    s.select_option(index=1)
                except Exception:
                    pass

        captura = hs.EVID / f"{slug}__{instancia}__{HOY}.png"
        raiz.screenshot(path=str(captura))
        fila["captura"] = captura.name

        if hs.DRY_RUN:
            fila["error"] = "DRY_RUN=1: no se envio"
            return fila

        raiz.locator("input[type='submit'], button[type='submit']").first.click()
        pg.wait_for_timeout(6000)
        txt = raiz.inner_text().lower()
        fila["R3_envio"] = True
        fila["R4_confirmacion"] = ("gracias" in txt or "contactaremos" in txt)
        captura2 = hs.EVID / f"{slug}__{instancia}__{HOY}__post.png"
        raiz.screenshot(path=str(captura2))
        fila["captura_post"] = captura2.name
    except Exception as e:
        fila["error"] = f"{type(e).__name__}: {e}"[:250]
    return fila


with sync_playwright() as pw:
    nav = pw.chromium.launch()
    for pag in paginas:
        pg = nav.new_page()
        try:
            pg.goto(pag["url"], timeout=60000, wait_until="networkidle")
            pg.wait_for_timeout(5000)
            filas.append(completar_y_enviar(pg, pg, pag["slug"], "banner"))

            pg2 = nav.new_page()
            pg2.goto(pag["url"], timeout=60000, wait_until="networkidle")
            pg2.wait_for_timeout(3000)
            abierto = False
            for sel in ("text=Postula", "text=POSTULA", "a[href='#modalFormulario']", "[onclick*='openPostulaModal']"):
                loc = pg2.locator(sel).first
                if loc.count():
                    try:
                        loc.click(timeout=5000)
                        abierto = True
                        break
                    except Exception:
                        continue
            pg2.wait_for_timeout(5000)
            if abierto:
                filas.append(completar_y_enviar(pg2, pg2.locator("#hubspot-formulario"), pag["slug"], "modal"))
            else:
                filas.append({"slug": pag["slug"], "instancia": "modal", "R1_renderiza": False,
                              "error": "no se pudo abrir el modal", "fecha": hs.ahora(),
                              "dry_run": hs.DRY_RUN, "captura": None})
            pg2.close()
        except Exception as e:
            filas.append({"slug": pag["slug"], "instancia": "pagina", "error": str(e)[:200],
                          "fecha": hs.ahora(), "dry_run": hs.DRY_RUN, "captura": None})
        pg.close()
        print(f"{pag['slug']}: listo")
    nav.close()

# Verificacion en HubSpot de cada correo enviado
if not hs.DRY_RUN:
    time.sleep(20)
    for f in filas:
        if not f.get("correo") or not f.get("R3_envio"):
            continue
        r = hs.api("POST", "/crm/v3/objects/contacts/search", json={
            "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": f["correo"]}]}],
            "properties": ["email", "hs_object_id", "createdate"], "limit": 1})
        if r.status_code == 200 and r.json().get("results"):
            f["H1_contacto"] = True
            f["hs_object_id"] = r.json()["results"][0]["id"]
        else:
            f["H1_contacto"] = False
            f["hs_object_id"] = None

previo = {}
try:
    previo = hs.leer("30_envios.json")
except FileNotFoundError:
    pass
todas = {(x["slug"], x["instancia"]): x for x in previo.get("instancias", [])}
todas.update({(x["slug"], x["instancia"]): x for x in filas})

res = {"generado": hs.ahora(), "dry_run": hs.DRY_RUN,
       "instancias": sorted(todas.values(), key=lambda x: (x["slug"], x["instancia"]))}
print(hs.guardar("30_envios.json", res))
print(f"INSTANCIAS ACUMULADAS: {len(res['instancias'])}/80 · DRY_RUN={hs.DRY_RUN}")
