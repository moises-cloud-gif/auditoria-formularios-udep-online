#!/usr/bin/env python3
"""Estado HTTP actual de las URLs que el QA de agosto (planilla canon) marco como caidas, de
prueba o fuera de inventario, mas las 6 paginas de diplomados y la pagina -dev.
Solo HTTP contra udeponline.pe. Sale output/42_reconciliacion_agosto.json.
"""
import sys, pathlib, requests
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

URLS = {
    "negocios-innovadores (URL del canon, fila 35)": "https://udeponline.pe/negocios-innovadores/",
    "curso-de-negocios-innovadores (URL real)": "https://udeponline.pe/curso-de-negocios-innovadores/",
    "enfelicidad (URL mal escrita del canon, fila 19)": "https://udeponline.pe/programa-de-especializacion-enfelicidad-y-desarrollo-organizacional/",
    "felicidad-y-desarrollo (URL real)": "https://udeponline.pe/programa-de-especializacion-en-felicidad-y-desarrollo-organizacional/",
    "curso-de-marketing-digital-test (fila 34)": "https://udeponline.pe/curso-de-marketing-digital-test/",
    "programas-de-especializacion-dev": "https://udeponline.pe/programas-de-especializacion-dev/",
    "curso-de-analitica-digital-growth-marketing": "https://udeponline.pe/curso-de-analitica-digital-growth-marketing/",
}
for p in hs.paginas():
    if p["tipo"] == "diplomado":
        URLS[f"diplomado: {p['slug']}"] = p["url"]

res = {"generado": hs.ahora(), "urls": []}
for nombre, u in URLS.items():
    try:
        r = requests.get(u, timeout=30, allow_redirects=False)
        fila = {"nombre": nombre, "url": u, "http": r.status_code,
                "redirige_a": r.headers.get("Location"),
                "tiene_formulario": "hbspt.forms.create" in r.text if r.status_code == 200 else None}
        if r.status_code in (301, 302, 307, 308):
            r2 = requests.get(u, timeout=30, allow_redirects=True)
            fila["destino_final"] = r2.url; fila["http_final"] = r2.status_code
    except Exception as e:
        fila = {"nombre": nombre, "url": u, "error": str(e)[:100]}
    res["urls"].append(fila)
    print(f"{fila.get('http', 'ERR')} {'-> ' + str(fila.get('redirige_a')) if fila.get('redirige_a') else ''} | {nombre}")
print(hs.guardar("42_reconciliacion_agosto.json", res))
