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
paginas = hs.paginas()[a.desde:a.hasta]
filas = []


def _frames_con_formulario(pg):
    """Devuelve [(frame, es_del_modal)] de los marcos que contienen un formulario.

    No depende de marcar el iframe con un atributo: HubSpot vuelve a dibujar el iframe
    despues de cargar y borra cualquier marca, que es lo que hacia fallar el llenado.
    Un objeto Frame de Playwright se puede volver a buscar en cada accion.
    """
    salida = []
    for fr in pg.frames:
        if fr == pg.main_frame:
            continue
        try:
            if fr.locator("form").count() == 0:
                continue
            el = fr.frame_element()
            es_modal = bool(el.evaluate("el => !!el.closest('#hubspot-formulario')"))
            salida.append((fr, es_modal))
        except Exception:
            continue
    return salida


def buscar_frame(pg, instancia):
    """Marco del formulario del banner o del modal. Lanza excepcion si no aparece."""
    cands = _frames_con_formulario(pg)
    if not cands:
        raise RuntimeError(f"ningun marco con formulario en la pagina (marcos totales: {len(pg.frames) - 1})")
    quiero_modal = instancia == "modal"
    exactos = [f for f, m in cands if m == quiero_modal]
    if exactos:
        return exactos[0]
    if len(cands) == 1:
        return cands[0][0]
    raise RuntimeError(f"no se distinguio el marco de '{instancia}' entre {len(cands)} candidatos")


def marcar_iframes(pg):
    """Compatibilidad: informa cuantos marcos de formulario hay."""
    return len(_frames_con_formulario(pg))


def con_reintento(fn, pg, intentos=4, espera=2000):
    """Ejecuta fn() y reintenta si el marco se renovo en el medio."""
    ultimo = None
    for _ in range(intentos):
        try:
            return fn()
        except Exception as e:
            ultimo = e
            pg.wait_for_timeout(espera)
    raise ultimo


def completar_y_enviar(pg, instancia, slug):
    """Llena y envia el formulario dentro de su marco. Devuelve la fila de evidencia."""
    correo = hs.correo_qa(slug, instancia, HOY)
    fila = {"slug": slug, "instancia": instancia, "correo": correo,
            "fecha": hs.ahora(), "dry_run": hs.DRY_RUN,
            "R1_renderiza": False, "R2_campos": [], "R3_envio": False,
            "R4_confirmacion": False, "R5_clausula_datos": False,
            "recaptcha_clave_de_prueba": None, "form_id_disparado": None,
            "campos_llenados": [], "campos_no_llenados": [], "errores_de_validacion": [],
            "captura": None, "error": None}
    try:
        con_reintento(lambda: buscar_frame(pg, instancia).locator("form").first.wait_for(
            state="visible", timeout=15000), pg)
        fila["R1_renderiza"] = True
        pg.wait_for_timeout(3000)   # deja que HubSpot termine de re-dibujar

        fila["R2_campos"] = con_reintento(lambda: buscar_frame(pg, instancia).locator(
            "form input, form select, form textarea").evaluate_all(
            "els => els.map(e => e.name || e.id).filter(Boolean)"), pg)
        fila["form_id_disparado"] = con_reintento(lambda: buscar_frame(pg, instancia).locator(
            "form").first.get_attribute("data-form-id"), pg)
        texto = con_reintento(lambda: buscar_frame(pg, instancia).locator("body").inner_text(), pg).lower()
        fila["R5_clausula_datos"] = ("autorizo" in texto or "datos personales" in texto or "autoriza" in texto)
        fila["recaptcha_clave_de_prueba"] = "testing purposes only" in texto

        def anotar(nombre, ok):
            (fila["campos_llenados"] if ok else fila["campos_no_llenados"]).append(nombre)
            return ok

        def llenar(sel_campo, val, nombre=None, obligatorio=True):
            nombre = nombre or sel_campo
            def _hacer():
                loc = buscar_frame(pg, instancia).locator(sel_campo).first
                if loc.count() == 0:
                    return None
                loc.fill(val, timeout=8000)
                return loc.input_value()
            try:
                puesto = con_reintento(_hacer, pg)
                if puesto is None:
                    return anotar(nombre, False)
                if not puesto:   # quedo vacio: el campo necesita tecleo, no pegado
                    def _teclear():
                        l2 = buscar_frame(pg, instancia).locator(sel_campo).first
                        l2.click(timeout=6000)
                        l2.type(val, delay=40, timeout=10000)
                        return l2.input_value()
                    puesto = con_reintento(_teclear, pg, intentos=2)
                return anotar(nombre, bool(puesto))
            except Exception:
                if obligatorio:
                    return anotar(nombre, False)
                return anotar(nombre, False)

        def elegir(sel_campo, nombre=None):
            """Elige la primera opcion real del desplegable (salteando el 'Selecciona')."""
            nombre = nombre or sel_campo
            def _hacer():
                d = buscar_frame(pg, instancia).locator(sel_campo).first
                if d.count() == 0:
                    return None
                valores = d.locator("option").evaluate_all(
                    "els => els.map(e => e.value).filter(v => v !== null && v !== '')")
                if not valores:
                    return None
                d.select_option(value=valores[0], timeout=8000)
                return d.input_value()
            try:
                puesto = con_reintento(_hacer, pg)
                return anotar(nombre, bool(puesto))
            except Exception:
                return anotar(nombre, False)

        llenar("input[name='firstname']", "QA", "nombre")
        llenar("input[name='lastname']", f"Prueba {slug[:40]}", "apellido")
        llenar("input[name='email']", correo, "correo")
        # ---- telefono ---------------------------------------------------------------
        # Es un campo internacional: al lado del selector de pais hay un input que filtra
        # lo que se pega. Se prueban varios selectores, se teclea, y como ultimo recurso se
        # escribe el valor disparando los eventos que el widget escucha.
        solo_numero = "".join(c for c in hs.QA_TEL if c.isdigit())[-9:]

        def llenar_telefono():
            candidatos = ("input[name='phone']", "input[type='tel']",
                          ".hs-fieldtype-intl-phone input.hs-input",
                          ".hs_phone input.hs-input:not([type='hidden'])")
            for sel_tel in candidatos:
                try:
                    fr = buscar_frame(pg, instancia)
                    loc = fr.locator(sel_tel).first
                    if loc.count() == 0 or not loc.is_visible():
                        continue
                    # 1) pegar
                    try:
                        loc.fill(solo_numero, timeout=6000)
                        if loc.input_value().strip():
                            return anotar(f"telefono ({sel_tel})", True)
                    except Exception:
                        pass
                    # 2) teclear
                    try:
                        loc.click(timeout=5000)
                        loc.press_sequentially(solo_numero, delay=60, timeout=10000)
                        if loc.input_value().strip():
                            return anotar(f"telefono ({sel_tel})", True)
                    except Exception:
                        try:
                            loc.type(solo_numero, delay=60, timeout=10000)
                            if loc.input_value().strip():
                                return anotar(f"telefono ({sel_tel})", True)
                        except Exception:
                            pass
                    # 3) escribir el valor y avisarle al widget
                    try:
                        loc.evaluate("""(el, v) => {
                            el.focus();
                            el.value = v;
                            el.dispatchEvent(new Event('input', {bubbles: true}));
                            el.dispatchEvent(new Event('change', {bubbles: true}));
                            el.dispatchEvent(new Event('blur', {bubbles: true}));
                        }""", solo_numero)
                        if loc.input_value().strip():
                            return anotar(f"telefono ({sel_tel})", True)
                    except Exception:
                        pass
                except Exception:
                    continue
            return anotar("telefono", False)

        con_reintento(llenar_telefono, pg, intentos=2)
        for s_campo, nom in (("textarea[name='mensaje']", "mensaje"),
                             ("textarea[name='message']", "mensaje generico"),
                             ("textarea[name='mensaje__udn_udep_']", "mensaje con sufijo")):
            if buscar_frame(pg, instancia).locator(s_campo).count():
                llenar(s_campo, f"PRUEBA QA 5MINUTOS - {HOY} - NO GESTIONAR", nom, obligatorio=False)
        elegir("select[name^='nivel_de_estudios']", "nivel de estudios")
        elegir("select[name^='medio_de_contacto']", "medio de contacto")
        for s_campo in ("input[type='checkbox'][name*='LEGAL']", "input[type='checkbox'][name*='consent']"):
            try:
                def _chk():
                    c = buscar_frame(pg, instancia).locator(s_campo).first
                    if c.count() and not c.is_checked():
                        c.check(timeout=6000)
                    return True
                con_reintento(_chk, pg, intentos=2)
            except Exception:
                pass

        captura = hs.EVID / f"{slug}__{instancia}__{HOY}.png"
        try:
            con_reintento(lambda: buscar_frame(pg, instancia).frame_element().screenshot(path=str(captura)), pg, intentos=2)
        except Exception:
            pg.screenshot(path=str(captura))
        fila["captura"] = captura.name

        if hs.DRY_RUN:
            fila["error"] = "DRY_RUN=1: no se envio"
            return fila

        con_reintento(lambda: buscar_frame(pg, instancia).locator(
            "input[type='submit'], button[type='submit']").first.click(timeout=12000), pg)
        pg.wait_for_timeout(9000)
        # Errores de validacion: si el formulario rechazo el envio, siguen los campos en pantalla.
        try:
            fila["errores_de_validacion"] = buscar_frame(pg, instancia).locator(
                ".hs-error-msg, .hs-main-font-element label.hs-error-msg").all_inner_texts()
        except Exception:
            pass
        t2 = ""
        try:
            t2 = buscar_frame(pg, instancia).locator("body").inner_text().lower()
        except Exception:
            pass
        if not t2:
            t2 = pg.locator("body").inner_text().lower()
        fila["R4_confirmacion"] = ("gracias" in t2 or "contactaremos" in t2)
        # R3 es "el envio se acepto", no "se apreto el boton".
        fila["R3_envio"] = bool(fila["R4_confirmacion"]) or not fila["errores_de_validacion"]
        if fila["errores_de_validacion"]:
            fila["error"] = "el formulario rechazo el envio: " + " | ".join(fila["errores_de_validacion"])[:180]
        fila["texto_despues_de_enviar"] = t2[:200]
        captura2 = hs.EVID / f"{slug}__{instancia}__{HOY}__post.png"
        try:
            buscar_frame(pg, instancia).frame_element().screenshot(path=str(captura2))
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
            elif marcar_iframes(pg2) == 0:
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
