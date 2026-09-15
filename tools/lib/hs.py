"""Cliente minimo de HubSpot con guarda de portal y registro de evidencia.

Regla del proyecto: ningun agente llama a la API a mano. Todo pasa por aca,
porque aca viven la guarda de portal, el backoff y el guardado de la respuesta cruda.
"""
import json, os, pathlib, time, datetime
import requests
from dotenv import load_dotenv

RAIZ = pathlib.Path(__file__).resolve().parents[2]
load_dotenv(RAIZ / ".env")

TOKEN = os.getenv("HUBSPOT_TOKEN", "").strip()
PORTAL = os.getenv("HUBSPOT_PORTAL_ID", "6925781").strip()
DRY_RUN = os.getenv("DRY_RUN", "1").strip() == "1"
QA_BASE = os.getenv("QA_EMAIL_BASE", "qa@5minutos.io").strip()
QA_TEL = os.getenv("QA_TELEFONO", "+51900000000").strip()

OUT = RAIZ / "output"
EVID = OUT / "evidencia"
OUT.mkdir(exist_ok=True)
EVID.mkdir(exist_ok=True)

BASE = "https://api.hubapi.com"
ESCRITURA = {"POST", "PUT", "PATCH", "DELETE"}
RUTAS_ESCRITURA_PERMITIDAS = ("/crm/v3/objects/contacts/batch/archive",)
# POST que en realidad son lecturas. La API de HubSpot usa POST para buscar.
RUTAS_POST_DE_LECTURA = ("/crm/v3/objects/contacts/search", "/crm/v3/objects/deals/search")


class SinToken(Exception):
    pass


class PortalEquivocado(Exception):
    pass


def _headers():
    if not TOKEN:
        raise SinToken(
            "HUBSPOT_TOKEN vacio. Copia .env.example a .env y pone el token de la private app. "
            "Sin eso no se puede verificar nada y el flujo debe detenerse."
        )
    return {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}


_portal_verificado = False


def guarda_portal():
    """Aborta si el token no es del portal 6925781. Se corre una sola vez por proceso."""
    global _portal_verificado
    if _portal_verificado:
        return
    r = requests.get(f"{BASE}/account-info/v3/details", headers=_headers(), timeout=20)
    r.raise_for_status()
    devuelto = str(r.json().get("portalId"))
    if devuelto != PORTAL:
        raise PortalEquivocado(
            f"El token responde al portal {devuelto} y este proyecto solo opera sobre {PORTAL}."
        )
    _portal_verificado = True


def api(metodo, ruta, **kw):
    """Llamada a la API con guarda de portal, backoff ante 429 y sin excepcion por 4xx."""
    guarda_portal()
    metodo = metodo.upper()
    es_lectura_disfrazada = metodo == "POST" and any(ruta.startswith(p) for p in RUTAS_POST_DE_LECTURA)
    if metodo in ESCRITURA and not es_lectura_disfrazada \
            and not any(ruta.startswith(p) for p in RUTAS_ESCRITURA_PERMITIDAS):
        raise PermissionError(
            f"Escritura no contemplada: {metodo} {ruta}. La auditoria es de solo lectura "
            "salvo el envio publico de formularios y la limpieza final."
        )
    url = ruta if ruta.startswith("http") else BASE + ruta
    for intento in range(5):
        r = requests.request(metodo, url, headers=_headers(), timeout=40, **kw)
        if r.status_code == 429:
            time.sleep(2 ** intento)
            continue
        return r
    return r


def ahora():
    return datetime.datetime.now().isoformat(timespec="seconds")


def guardar(nombre, data):
    p = OUT / nombre
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(p.relative_to(RAIZ))


def leer(nombre):
    p = OUT / nombre
    if not p.exists():
        raise FileNotFoundError(f"Falta {nombre}. Corre la ronda que lo produce antes de esta.")
    return json.loads(p.read_text(encoding="utf-8"))


def paginas():
    p = RAIZ / "input" / "paginas.json"
    return json.loads(p.read_text(encoding="utf-8"))["paginas"]


def correo_qa(slug, instancia, fecha=None):
    fecha = fecha or datetime.date.today().strftime("%Y%m%d")
    usuario, dominio = QA_BASE.split("@", 1)
    return f"{usuario}+{slug}-{instancia}-{fecha}@{dominio}"
