#!/usr/bin/env python3
"""Diagnostico para cuando el preflight falla. No necesita token.

1. Revisa si el archivo .env existe, donde esta y si la variable se carga (sin mostrar el token).
2. Detecta el error clasico de Windows: el Bloc de notas guarda ".env" como ".env.txt".
3. Abre una pagina real y cuenta los campos del formulario DENTRO del iframe de HubSpot,
   que es donde viven de verdad. Guarda captura y HTML en output/evidencia/.
"""
import os, sys, pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[1]
print("=" * 70)
print("1. ARCHIVO DE CONFIGURACION (.env)")
print("=" * 70)
print(f"Carpeta del proyecto: {RAIZ}")
env = RAIZ / ".env"
print(f".env existe: {'SI' if env.exists() else 'NO'}")
if env.exists():
    print(f".env tamano: {env.stat().st_size} bytes")

parecidos = [p.name for p in RAIZ.iterdir() if p.is_file() and p.name.lower().startswith(".env")]
print(f"Archivos que empiezan con .env en la carpeta: {parecidos or 'ninguno'}")
for mal in (".env.txt", ".env.example.txt", "env", "env.txt"):
    if (RAIZ / mal).exists():
        print(f"  !! ATENCION: existe '{mal}'. Windows lo guardo con extension .txt.")
        print(f"     Renombralo a '.env' exacto (sin .txt).")

try:
    from dotenv import load_dotenv
    load_dotenv(env)
    tok = (os.getenv("HUBSPOT_TOKEN") or "").strip()
    portal = (os.getenv("HUBSPOT_PORTAL_ID") or "").strip()
    dry = (os.getenv("DRY_RUN") or "").strip()
    if tok:
        print(f"HUBSPOT_TOKEN: cargado · empieza con '{tok[:7]}...' · {len(tok)} caracteres")
        if not tok.startswith("pat-"):
            print("  !! El token no empieza con 'pat-'. Revisa que sea el de la private app.")
        if tok.startswith('"') or tok.endswith('"'):
            print("  !! El token tiene comillas. Sacaselas.")
    else:
        print("HUBSPOT_TOKEN: VACIO  <-- esta es la causa de las FALLAS P1 a P4")
    print(f"HUBSPOT_PORTAL_ID: {portal or 'VACIO'}")
    print(f"DRY_RUN: {dry or 'VACIO'}")
except ImportError:
    print("Falta la libreria python-dotenv. Corre: pip install -r requirements.txt")

print()
print("=" * 70)
print("2. RENDERIZADO DEL FORMULARIO (no necesita token)")
print("=" * 70)
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright no esta instalado. Corre: pip install -r requirements.txt")
    sys.exit(0)

# Se puede pasar otra URL como argumento, por ejemplo una pagina de UANDES Online,
# para comparar si la clave del reCAPTCHA es la misma (o sea, si es de portal).
url = sys.argv[1] if len(sys.argv) > 1 else "https://udeponline.pe/curso-de-gestion-del-talento/"
visible = os.getenv("PW_VISIBLE", "0") == "1"
evid = RAIZ / "output" / "evidencia"
evid.mkdir(parents=True, exist_ok=True)

with sync_playwright() as pw:
    nav = pw.chromium.launch(headless=not visible)
    ctx = nav.new_context(viewport={"width": 1440, "height": 900}, locale="es-PE")
    pg = ctx.new_page()
    print(f"Abriendo {url} (navegador {'visible' if visible else 'oculto'})...")
    pg.goto(url, timeout=90000, wait_until="domcontentloaded")
    pg.wait_for_timeout(9000)
    print(f"  titulo de la pagina: {pg.title()[:70]}")
    print(f"  campos en la pagina principal: {pg.locator('form input').count()}  <-- por esto fallaba P5")
    print(f"  marcos (iframes) en la pagina: {len(pg.frames) - 1}")
    total = 0
    for fr in pg.frames[1:]:
        n = fr.locator("input, select, textarea").count()
        total += n
        if n:
            print(f"    marco con {n} campos · url: {(fr.url or 'sin url')[:60]}")
    print(f"  CAMPOS REALES DENTRO DE LOS MARCOS: {total}")
    ifr = pg.locator("iframe.hs-form-iframe, iframe[id^='hs-form-iframe']").count()
    print(f"  iframes de formulario de HubSpot detectados: {ifr}")
    txt = pg.content()
    # reCAPTCHA: la clave (sitekey) viaja en la URL del marco de Google, parametro k=
    import re as _re
    CLAVE_PRUEBA_GOOGLE = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
    claves = set()
    for fr in pg.frames:
        m = _re.search(r"[?&]k=([A-Za-z0-9_\-]+)", fr.url or "")
        if m:
            claves.add(m.group(1))
    if claves:
        tipo = "enterprise" if any("enterprise" in (f.url or "") for f in pg.frames) else "clasico"
        for k in claves:
            print(f"  reCAPTCHA sitekey ({tipo}): {k}")
            if k == CLAVE_PRUEBA_GOOGLE:
                print("     !! ES LA CLAVE DE PRUEBA PUBLICA DE GOOGLE: no hay proteccion real contra spam")
            else:
                print("     (no es la clave de prueba publica de Google; comparar con la del portal en HubSpot)")
    else:
        print("  no se detecto ningun marco de reCAPTCHA")
    aviso = "testing purposes only" in txt.lower()
    for fr in pg.frames:
        try:
            if "testing purposes only" in fr.locator("body").inner_text().lower():
                aviso = True
        except Exception:
            pass
    print(f"  aviso 'This reCAPTCHA is for testing purposes only' visible: {aviso}")
    print(f"  Cloudflare desafiando: {'just a moment' in pg.title().lower() or 'checking your browser' in txt.lower()}")
    pg.screenshot(path=str(evid / "diagnostico_render.png"), full_page=False)
    (evid / "diagnostico_render.html").write_text(txt, encoding="utf-8")
    print(f"  captura: output/evidencia/diagnostico_render.png")
    nav.close()

print()
print("Si 'CAMPOS REALES DENTRO DE LOS MARCOS' es mayor que 0, el sitio esta bien y el")
print("problema era solo que los scripts buscaban los campos en el lugar equivocado.")
print()
print("Para comparar el reCAPTCHA con UANDES Online (y saber si la clave es de portal):")
print("  python tools/diagnostico.py https://uandesonline.cl/producto/diplomado-en-marketing-digital-e-commerce/")
print("Si la sitekey es la misma que la de UDEP, la clave es del portal 6925781 y el")
print("problema alcanza tambien a los formularios de UANDES: avisarle a Rocio.")
