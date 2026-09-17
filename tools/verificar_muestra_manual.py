#!/usr/bin/env python3
"""Verifica en HubSpot los envios manuales de la muestra (output/muestra_envios_manuales.csv).

Solo lectura. Por cada correo qa+mN-... busca el contacto, guarda la respuesta cruda en
output/evidencia/contactos/ y arma output/51_muestra_manual_resultados.json con:

  H1  el contacto existe y es un registro propio (no fusionado con otro envio)
  H2  atribucion: el formulario que HubSpot registro como conversion
  H3  programa que llego vs el que corresponde a la pagina
  H5  propietario asignado (efecto del Activador). Debe ser de 5minutos.
  control MQL: las propiedades de MQL deben quedar vacias

HubSpot graba el evento de conversion como "Titulo de la pagina: Nombre del formulario",
asi que la comparacion de H2 acepta que el nombre esperado sea el sufijo.

Uso: python3 tools/verificar_muestra_manual.py
"""
import sys, pathlib, json, csv
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

RAW = hs.EVID / "contactos"
RAW.mkdir(parents=True, exist_ok=True)

PROPS = ["email", "firstname", "lastname", "phone", "createdate", "hs_object_id",
         "hubspot_owner_id", "hubspot_owner_assigneddate",
         "recent_conversion_event_name", "recent_conversion_date",
         "first_conversion_event_name", "num_conversion_events",
         "cursos_piura__udn_udep_", "programas_piura__udn_udep_", "cursos_piura",
         "mensaje", "message", "medio_de_contacto__udn_udep_", "nivel_de_estudios__udn_udep_",
         "hs_analytics_first_url", "hs_analytics_source", "lifecyclestage",
         "equipos_por_nivel_de_estudios__udn_udep_", "facultades_piura__udn_udep_",
         "pais_lead", "programa_mas_recientemente_solicitado", "estatus_de_gestion",
         "mql__si_o_no_", "mql_aplica_10"]

r = hs.api("GET", "/crm/v3/owners?limit=500")
DUENOS = {str(o["id"]): (o.get("email") or "") for o in r.json().get("results", [])} if r.status_code == 200 else {}
NUESTROS = {i for i, e in DUENOS.items() if "5minutos" in e.lower()}
print(f"propietarios del portal: {len(DUENOS)} · de 5minutos: {len(NUESTROS)}")

csv_path = hs.OUT / "muestra_envios_manuales.csv"
filas = list(csv.DictReader(csv_path.read_text(encoding="utf-8-sig").splitlines()))

forms = hs.leer("11_formularios.json")["formularios"]
def esperado_de(slug):
    return next((f["nombre"] for f in forms.values() if f.get("slug") == slug), None)

def norm(s):
    return " ".join((s or "").lower().split())

def atribuye(registrado, esperado):
    """HubSpot antepone el titulo de la pagina: 'Titulo: Nombre del formulario'."""
    if not registrado or not esperado:
        return None
    a, b = norm(registrado), norm(esperado)
    return a == b or a.endswith(": " + b)

salida, ids = [], {}
for f in filas:
    correo = f["correo_a_usar"]
    slug = f["pagina"].rstrip("/").rsplit("/", 1)[-1]
    if f["codigo"] == "m1":                       # m1 se envio con el correo de referencia
        correo = "qa+manual-20260917@5minutos.io"
    res = hs.api("POST", "/crm/v3/objects/contacts/search", json={
        "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": correo}]}],
        "properties": PROPS, "limit": 1})
    fila = {"codigo": f["codigo"], "slug": slug, "instancia_planeada": f["instancia"],
            "correo": correo, "pagina": f["pagina"]}
    if res.status_code != 200 or not res.json().get("results"):
        fila.update({"H1_contacto": False, "contacto": None,
                     "detalle": f"sin contacto (HTTP {res.status_code})"})
        salida.append(fila); print(f"  {f['codigo']:3} SIN CONTACTO  {correo}")
        continue
    c = res.json()["results"][0]
    (RAW / f"{c['id']}.json").write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    p = c.get("properties", {})
    dueno = str(p.get("hubspot_owner_id") or "")
    conv = p.get("recent_conversion_event_name") or p.get("first_conversion_event_name")
    esp = esperado_de(slug)
    fila.update({
        "H1_contacto": True,
        "contacto": c["id"],
        "creado": p.get("createdate"),
        "nombre": f"{p.get('firstname') or ''} {p.get('lastname') or ''}".strip(),
        "telefono": p.get("phone"),
        "H2_formulario_registrado": conv,
        "H2_formulario_esperado": esp,
        "H2_atribucion": atribuye(conv, esp),
        "conversiones": p.get("num_conversion_events"),
        "url_de_origen": p.get("hs_analytics_first_url"),
        "H3_programa_que_llego": p.get("cursos_piura__udn_udep_") or p.get("programas_piura__udn_udep_") or p.get("cursos_piura"),
        "H5_propietario": dueno or None,
        "H5_propietario_email": DUENOS.get(dueno),
        "H5_disparo": bool(dueno),
        "fuga_a_ejecutivo_real": bool(dueno) and dueno not in NUESTROS,
        "equipo": p.get("equipos_por_nivel_de_estudios__udn_udep_"),
        "facultad": p.get("facultades_piura__udn_udep_"),
        "pais": p.get("pais_lead"),
        "programa_mas_reciente": p.get("programa_mas_recientemente_solicitado"),
        "estatus_de_gestion": p.get("estatus_de_gestion"),
        "nivel_de_estudios": p.get("nivel_de_estudios__udn_udep_"),
        "medio_de_contacto": p.get("medio_de_contacto__udn_udep_"),
        "mensaje": p.get("mensaje") or p.get("message"),
        "mql_si_o_no": p.get("mql__si_o_no_"),
        "mql_aplica_10": p.get("mql_aplica_10"),
        "ciclo_de_vida": p.get("lifecyclestage"),
    })
    ids.setdefault(c["id"], []).append(f["codigo"])
    salida.append(fila)
    print(f"  {f['codigo']:3} {c['id']:>14}  dueno={DUENOS.get(dueno) or '(sin asignar)':30} "
          f"prog={str(fila['H3_programa_que_llego'])[:28]:28} mql={p.get('mql__si_o_no_')}")

# contactos fusionados: mismo id para mas de un codigo => la cookie volvio a unirlos
for cid, cods in ids.items():
    if len(cods) > 1:
        for fila in salida:
            if fila.get("contacto") == cid:
                fila["registro_fusionado_con"] = [c for c in cods if c != fila["codigo"]]

hs.guardar("51_muestra_manual_resultados.json", {
    "generado": hs.ahora(),
    "que_es": "Envios hechos a mano por Moises Camargo, uno por ventana de incognito.",
    "contactos_distintos": len(ids),
    "resultados": salida,
})
print(f"\ncontactos distintos: {len(ids)} (si es menor que los envios con contacto, hubo fusion)")
print("guardado: output/51_muestra_manual_resultados.json")
