#!/usr/bin/env python3
"""Escaneo defensivo del HTML crudo de las 40 paginas (output/evidencia/paginas/*.html).

Busca indicadores de scripts de verificacion falsa tipo ClickFix (dominio id-verif-code.info,
textos de "verificacion humana" fuera de un reCAPTCHA legitimo, escritura al portapapeles,
comandos de PowerShell/mshta/cmd, eval sobre base64) y lista todos los dominios externos desde
los que cada pagina carga scripts o iframes. No consulta HubSpot. Sale output/40_seguridad.json.
"""
import sys, pathlib, re, json, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

CARPETA = hs.EVID / "paginas"
INDICADORES = {
    "dominio_id-verif-code": re.compile(r"id-verif-code\.info", re.I),
    "verificacion_humana_texto": re.compile(r"verify (that )?you are (a )?human|i'?m not a robot|verificaci[oó]n humana|no soy un robot", re.I),
    "portapapeles": re.compile(r"navigator\.clipboard\.writeText|execCommand\(\s*['\"]copy", re.I),
    "comandos_windows": re.compile(r"powershell|mshta|cmd\.exe|/c\s+start|rundll32|Win\s*\+\s*R", re.I),
    "eval_base64": re.compile(r"eval\s*\(\s*atob|atob\s*\([^)]{40,}\)\s*\)\s*;?\s*eval|document\.write\(\s*unescape", re.I),
    "script_ofuscado_largo": re.compile(r"<script[^>]*>[^<]{0,50}(?:\\x[0-9a-f]{2}){20,}", re.I),
}
LEGITIMOS = {"udeponline.pe", "www.udeponline.pe", "js.hsforms.net", "js.hs-scripts.com", "js.hs-analytics.net",
             "js.hs-banner.com", "js.hscollectedforms.net", "js.usemessages.com", "forms.hsforms.com",
             "www.googletagmanager.com", "www.google-analytics.com", "www.google.com", "www.gstatic.com",
             "connect.facebook.net", "www.facebook.com", "fonts.googleapis.com", "fonts.gstatic.com",
             "cdnjs.cloudflare.com", "static.cloudflareinsights.com", "challenges.cloudflare.com",
             "www.youtube.com", "player.vimeo.com", "cdn.jsdelivr.net", "ajax.googleapis.com",
             "static.hsappstatic.net", "www.clarity.ms", "snap.licdn.com", "analytics.tiktok.com",
             "www.googleadservices.com", "googleads.g.doubleclick.net", "stats.g.doubleclick.net"}
SRC = re.compile(r"<(script|iframe)[^>]+src\s*=\s*['\"]([^'\"]+)['\"]", re.I)
HOST = re.compile(r"^(?:https?:)?//([^/'\"\s?#]+)", re.I)

res = {"generado": hs.ahora(), "paginas": [], "resumen": {}}
dominios_globales = collections.Counter()
for html_path in sorted(CARPETA.glob("*.html")):
    html = html_path.read_text(encoding="utf-8", errors="replace")
    hallazgos = {}
    for nombre, rx in INDICADORES.items():
        m = list(rx.finditer(html))
        if m:
            ctx = html[max(0, m[0].start() - 80): m[0].end() + 80].replace("\n", " ")
            hallazgos[nombre] = {"ocurrencias": len(m), "contexto": ctx}
    externos = collections.Counter()
    for tag, src in SRC.findall(html):
        h = HOST.match(src.strip())
        if h:
            dominio = h.group(1).lower()
            if dominio not in LEGITIMOS:
                externos[dominio] += 1
    dominios_globales.update(externos.keys())
    # reCAPTCHA legitimo de HubSpot: no es hallazgo, solo se anota si aparece
    recaptcha = bool(re.search(r"recaptcha|grecaptcha", html, re.I))
    res["paginas"].append({
        "slug": html_path.stem, "bytes": len(html),
        "indicadores": hallazgos, "sospechosa": bool(hallazgos),
        "dominios_no_reconocidos": dict(externos), "menciona_recaptcha_en_html": recaptcha,
        "scripts_inline": len(re.findall(r"<script(?![^>]*\bsrc=)[^>]*>", html, re.I)),
    })

sosp = [p["slug"] for p in res["paginas"] if p["sospechosa"]]
res["resumen"] = {
    "paginas_escaneadas": len(res["paginas"]),
    "paginas_con_indicadores": sosp,
    "indicadores_hallados": dict(collections.Counter(k for p in res["paginas"] for k in p["indicadores"])),
    "dominios_no_reconocidos": dict(dominios_globales),
}
print(hs.guardar("40_seguridad.json", res))
print(f"PAGINAS ESCANEADAS: {len(res['paginas'])}")
print(f"CON INDICADORES CLICKFIX: {len(sosp)} -> {sosp}")
print(f"INDICADORES: {res['resumen']['indicadores_hallados']}")
print(f"DOMINIOS EXTERNOS NO RECONOCIDOS (en cuantas paginas): {dict(dominios_globales)}")

# ---- Segunda pasada: los scripts propios del sitio (wp-content, wp-includes, etc.) --------------
# Una inyeccion tipo ClickFix suele vivir en un .js del tema o de un plugin, no en el HTML.
import requests, hashlib
SCRIPTS = hs.EVID / "scripts"
SCRIPTS.mkdir(parents=True, exist_ok=True)
urls = set()
for html_path in sorted(CARPETA.glob("*.html")):
    html = html_path.read_text(encoding="utf-8", errors="replace")
    for tag, src in SRC.findall(html):
        if tag.lower() != "script":
            continue
        s = src.strip()
        if s.startswith("/"):
            s = "https://udeponline.pe" + s
        h = HOST.match(s)
        if h and h.group(1).lower() in ("udeponline.pe", "www.udeponline.pe"):
            urls.add(s.split("#")[0])
scripts = []
for u in sorted(urls):
    try:
        r = requests.get(u, timeout=30)
        cuerpo = r.text if r.status_code == 200 else ""
    except Exception as e:
        scripts.append({"url": u, "error": str(e)[:100]}); continue
    nombre = hashlib.sha1(u.encode()).hexdigest()[:10] + "_" + u.rsplit("/", 1)[-1].split("?")[0][:60]
    (SCRIPTS / nombre).write_text(cuerpo, encoding="utf-8")
    hall = {n: len(rx.findall(cuerpo)) for n, rx in INDICADORES.items() if rx.search(cuerpo)}
    # URLs externas dentro del JS
    ext = sorted({m.lower() for m in re.findall(r"https?://([a-z0-9.-]+\.[a-z]{2,})", cuerpo, re.I)
                  if m.lower() not in LEGITIMOS and not m.lower().endswith(("w3.org", "schema.org", "wordpress.org",
                  "elementor.com", "jquery.com", "github.com", "githubusercontent.com", "gnu.org", "mozilla.org",
                  "gravatar.com", "wp.org", "google.com", "gstatic.com", "youtube.com", "vimeo.com", "facebook.com",
                  "hsforms.net", "hubspot.com", "hsforms.com", "cloudflare.com", "jsdelivr.net", "unpkg.com",
                  "googleapis.com", "opensource.org", "sizzlejs.com", "jquery.org", "bootcss.com", "getbootstrap.com",
                  "momentjs.com", "swiper.js", "swiperjs.com", "gsap.com", "greensock.com", "lodash.com",
                  "underscorejs.org", "jqueryui.com", "wp-admin", "example.com"))})
    scripts.append({"url": u, "http": r.status_code, "bytes": len(cuerpo), "archivo": nombre,
                    "indicadores": hall, "dominios_externos_en_js": ext[:15]})
res["scripts_propios"] = scripts
res["resumen"]["scripts_propios_escaneados"] = len(scripts)
res["resumen"]["scripts_propios_con_indicadores"] = [s["url"] for s in scripts if s.get("indicadores")]
hs.guardar("40_seguridad.json", res)
print(f"SCRIPTS PROPIOS ESCANEADOS: {len(scripts)}")
print(f"CON INDICADORES: {res['resumen']['scripts_propios_con_indicadores']}")
for s in scripts:
    if s.get("dominios_externos_en_js"):
        print("  dominios en", s["url"].rsplit("/",1)[-1][:50], "->", s["dominios_externos_en_js"][:8])
