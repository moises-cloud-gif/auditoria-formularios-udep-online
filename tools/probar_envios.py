#!/usr/bin/env python3
"""Ronda 3. Envio real con Playwright sobre banner y modal, y verificacion en HubSpot.

Uso:  python3 tools/probar_envios.py --desde 0 --hasta 10
      PW_VISIBLE=1 python3 tools/probar_envios.py --desde 0 --hasta 2   (navegador a la vista)

Con DRY_RUN=1 recorre y captura pantalla pero NO envia. Eso no cierra la ronda.

IMPORTANTE (corregido el 16-sep-2026): udeponline.pe usa el embed v2 de HubSpot
(js.hsforms.net/forms/embed/v2.js), que dibuja el formulario DENTRO DE UN IFRAME.
La version original del script buscaba los campos en la pagina principal, donde nunca
hay ninguno, asi que no habria podido llenar ni enviar ni una sola instancia.
Todo el trabajo se hace ahora dentro del marco del formulario.
"""
import os, sys, pathlib, argparse, datetime, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs
from playwright.sync_api import sync_playwright

ap = argparse.ArgumentParser()
ap.add_argument("--desde", type=int, default=0)
ap.add_argument("--hasta", type=int, default=40)
a = ap.parse_args()

HOY = datetime.date.today().strftime("%Y%m%d")
VISIBLE = os.getenv("PW_VISIBLE", "0") == "1"
SEL_IFRAME = "iframe.hs-form-iframe, iframe[id^='hs-form-iframe']"
paginas = hs.paginas()[a.desde:a.hasta]
filas = []


def marcar_iframes(pg):
    """Etiqueta cada iframe de formulario como 'banner' o 'modal' segun donde vive."""
    try:
        pg.eval_on_selector_all(SEL_IFRAME, """els => els.forEach(el => {
            el.setAttribute('data-qa-inst', el.closest('#hubspot-formulario') ? 'modal' : 'banner');
        })""")
    except Exception:
        pass
    return pg.locator(SEL_IFRAME).count()


def marco(pg, instancia):
    """Devuelve un acceso FRESCO al iframe del formulario.

    HubSpot vuelve a dibujar el iframe despues de cargar (prellenado de valores conocidos,
    reCAPTCHA), y eso borra la marca que le ponemos. Por eso se re-marca antes de cada accion
    en lugar de guardar una referencia, que es lo que hacia fallar el llenado con TimeoutError.
    """
    marcar_iframes(pg)
    return pg.frame_locator(f"iframe[data-qa-inst='{instancia}']")


def con_reintento(fn, intentos=3, espera=1500, pg=None):
    """Ejecuta fn() y reintenta si el iframe se renovo en el medio."""
    ultimo = None
    for _ in range(intentos):
        try:
            return fn()
        except Exception as e:
            ultimo = e
            if pg is not None:
                pg.wait_for_timeout(espera)
    raise ultimo


def completar_y_enviar(pg, instancia, slug):
    """Llena y envia el formulario dentro de su iframe. Devuelve la fila de evidencia."""
    correo = hs.correo_qa(slug, instancia, HOY)
    fila = {"slug": slug, "instancia": instancia, "correo": correo,
            "fecha": hs.ahora(), "dry_run": hs.DRY_RUN,
            "R1_renderiza": False, "R2_campos": [], "R3_envio": False,
            "R4_confirmacion": False, "R5_clausula_datos": False,
            "recaptcha_clave_de_prueba": None, "form_id_disparado": None,
            "captura": None, "error": None}
    sel = f"iframe[data-qa-inst='{instancia}']"
    try:
        con_reintento(lambda: marco(pg, instancia).locator("form").first.wait_for(
            state="visible", timeout=20000), pg=pg)
        fila["R1_renderiza"] = True
        pg.wait_for_timeout(2500)   # deja que termine de re-dibujarse antes de tocar nada

        fila["R2_campos"] = con_reintento(lambda: marco(pg, instancia).locator(
            "form input, form select, form textarea").evaluate_all(
            "els => els.map(e => e.name || e.id).filter(Boolean)"), pg=pg)
        fila["form_id_disparado"] = con_reintento(lambda: marco(pg, instancia).locator(
            "form").first.get_attribute("data-form-id"), pg=pg)
        texto = con_reintento(lambda: marco(pg, instancia).locator("body").inner_text(), pg=pg).lower()
        fila["R5_clausula_datos"] = ("autorizo" in texto or "datos personales" in texto or "autoriza" in texto)
        fila["recaptcha_clave_de_prueba"] = "testing purposes only" in texto

        def llenar(sel_campo, val):
            def _hacer():
                loc = marco(pg, instancia).locator(sel_campo).first
                if loc.count() == 0:
                    return False
                loc.fill(val, timeout=10000)
                return True
            return con_reintento(_hacer, pg=pg)

        def elegir(sel_campo):
            def _hacer():
                d = marco(pg, instancia).locator(sel_campo).first
                if d.count() == 0:
                    return False
                d.select_option(index=1, timeout=10000)
                return True
            try:
                return con_reintento(_hacer, pg=pg)
            except Exception:
                return False

        llenar("input[name='firstname']", "QA")
        llenar("input[name='lastname']", f"Prueba {slug[:40]}")
        llenar("input[name='email']", correo)
        llenar("input[name='phone']", hs.QA_TEL)
        for s_campo in ("textarea[name='mensaje']", "textarea[name='message']",
                        "textarea[name='mensaje__udn_udep_']"):
            try:
                llenar(s_campo, f"PRUEBA QA 5MINUTOS - {HOY} - NO GESTIONAR")
            except Exception:
                pass
        for s_campo in ("select[name^='nivel_de_estudios']", "select[name^='medio_de_contacto']"):
            elegir(s_campo)
        for s_campo in ("input[type='checkbox'][name*='LEGAL']", "input[type='checkbox'][name*='consent']"):
            try:
                def _chk():
                    c = marco(pg, instancia).locator(s_campo).first
                    if c.count() and not c.is_checked():
                        c.check(timeout=8000)
                    return True
                con_reintento(_chk, pg=pg)
            except Exception:
                pass

        captura = hs.EVID / f"{slug}__{instancia}__{HOY}.png"
        try:
            con_reintento(lambda: (marcar_iframes(pg), pg.locator(sel).first.screenshot(path=str(captura)))[1], pg=pg)
        except Exception:
            pg.screenshot(path=str(captura))
        fila["captura"] = captura.name

        if hs.DRY_RUN:
            fila["error"] = "DRY_RUN=1: no se envio"
            return fila

        con_reintento(lambda: marco(pg, instancia).locator(
            "input[type='submit'], button[type='submit']").first.click(timeout=15000), pg=pg)
        pg.wait_for_timeout(9000)
        fila["R3_envio"] = True
        try:
            t2 = marco(pg, instancia).locator("body").inner_text().lower()
        except Exception:
            t2 = ""
        if not t2:
            t2 = pg.locator("body").inner_text().lower()
        fila["R4_confirmacion"] = ("gracias" in t2 or "contactaremos" in t2)
        fila["texto_despues_de_enviar"] = t2[:200]
        captura2 = hs.EVID / f"{slug}__{instancia}__{HOY}__post.png"
        try:
            marcar_iframes(pg)
            pg.locator(sel).first.screenshot(path=str(captura2))
        except Exception:
            pg.screenshot(path=str(captura2))
        fila["captura_post"] = captura2.name
    except Exception as e:
        fila["error"] = f"{type(e).__name__}: {e}"[:250]
        try:
            captura = hs.EVID / f"{slug}__{instancia}__{HOY}.png"
            pg.screenshot(path=str(captura))
            fila["captura"] = captura.name
        except Exception:
            pass
    return fila


with sync_playwright() as pw:
    nav = pw.chromium.launch(headless=not VISIBLE)
    ctx = nav.new_context(viewport={"width": 1440, "height": 900}, locale="es-PE")
    for pag in paginas:
        slug = pag["slug"]
        # --- banner -------------------------------------------------------------
        pg = ctx.new_page()
        try:
            pg.goto(pag["url"], timeout=90000, wait_until="domcontentloaded")
            pg.wait_for_timeout(9000)
            n = marcar_iframes(pg)
            if n == 0:
                filas.append({"slug": slug, "instancia": "banner", "R1_renderiza": False,
                              "error": "no se encontro ningun iframe de formulario de HubSpot",
                              "fecha": hs.ahora(), "dry_run": hs.DRY_RUN, "captura": None})
            else:
                filas.append(completar_y_enviar(pg, "banner", slug))
        except Exception as e:
            filas.append({"slug": slug, "instancia": "banner", "error": str(e)[:200],
                          "fecha": hs.ahora(), "dry_run": hs.DRY_RUN, "captura": None})
        pg.close()

        # --- modal --------------------------------------------------------------
        pg2 = ctx.new_page()
        try:
            pg2.goto(pag["url"], timeout=90000, wait_until="domcontentloaded")
            pg2.wait_for_timeout(6000)
            abierto = False
            for s in ("a[href='#modalFormulario']", "[onclick*='openPostulaModal']",
                      "text=Postula aquí", "text=POSTULA AQUÍ", "text=Postula", "text=POSTULA"):
                loc = pg2.locator(s).first
                if loc.count():
                    try:
                        loc.click(timeout=6000)
                        abierto = True
                        break
                    except Exception:
                        continue
            pg2.wait_for_timeout(7000)
            marcar_iframes(pg2)
            if not abierto:
                filas.append({"slug": slug, "instancia": "modal", "R1_renderiza": False,
                              "error": "no se pudo abrir el modal (no se encontro el boton Postula)",
                              "fecha": hs.ahora(), "dry_run": hs.DRY_RUN, "captura": None})
            elif pg2.locator("iframe[data-qa-inst='modal']").count() == 0:
                filas.append({"slug": slug, "instancia": "modal", "R1_renderiza": False,
                              "error": "el modal abrio pero no hay formulario dentro de #hubspot-formulario",
                              "fecha": hs.ahora(), "dry_run": hs.DRY_RUN, "captura": None})
            else:
                filas.append(completar_y_enviar(pg2, "modal", slug))
        except Exception as e:
            filas.append({"slug": slug, "instancia": "modal", "error": str(e)[:200],
                          "fecha": hs.ahora(), "dry_run": hs.DRY_RUN, "captura": None})
        pg2.close()
        ultimas = [f for f in filas[-2:]]
        print(f"{slug}: banner R1={ultimas[0].get('R1_renderiza')} R3={ultimas[0].get('R3_envio')} · "
              f"modal R1={ultimas[1].get('R1_renderiza')} R3={ultimas[1].get('R3_envio')}")
    ctx.close()
    nav.close()

# Verificacion rapida en HubSpot de cada correo enviado (el detalle lo completa
# tools/verificar_contactos.py, que ademas resuelve H2 y H5).
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
enviadas = sum(1 for x in res["instancias"] if x.get("R3_envio"))
print(f"INSTANCIAS ACUMULADAS: {len(res['instancias'])}/80 · ENVIADAS: {enviadas} · DRY_RUN={hs.DRY_RUN}")
