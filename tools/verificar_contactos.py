#!/usr/bin/env python3
"""Ronda 3, segunda mitad. Para cada instancia enviada en output/30_envios.json, lee el contacto
de prueba en HubSpot (solo lectura) y completa:

  H1_contacto        el contacto existe (hs_object_id real)
  H2_atribucion      el ultimo evento de conversion del contacto es el formulario de la pagina
  H3_programa_real   valor que quedo en la propiedad de programa del contacto
  H5_disparo         el contacto tiene propietario asignado (efecto del Activador -> asignacion)
  form_id_registrado nombre del formulario que HubSpot registro como conversion

Usa las propiedades del contacto (recent_conversion_event_name, hubspot_owner_id, etc.). No modifica
nada. Guarda la respuesta cruda de cada contacto en output/evidencia/contactos/<id>.json y
actualiza 30_envios.json. Correr despues de cada tanda de probar_envios.py, o al final.
"""
import sys, pathlib, json, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from lib import hs

RAW = hs.EVID / "contactos"
RAW.mkdir(parents=True, exist_ok=True)

# Propietarios de 5minutos: a uno de ellos deben quedar asignados los contactos de prueba,
# por acuerdo con Pedro. Si alguno cae en un propietario distinto, es una fuga a un
# ejecutivo real y hay que detener la pasada.
def _cargar_propietarios():
    r = hs.api("GET", "/crm/v3/owners?limit=500")
    todos = {str(o.get("id")): (o.get("email") or "") for o in r.json().get("results", [])} if r.status_code == 200 else {}
    nuestros = {i for i, e in todos.items() if "5minutos" in e.lower()}
    return todos, nuestros

PROPIETARIOS, NUESTROS = _cargar_propietarios()
print(f"propietarios del portal leidos: {len(PROPIETARIOS)} · de 5minutos: {len(NUESTROS)}")
forms = hs.leer("11_formularios.json")["formularios"]
envios = hs.leer("30_envios.json")
PROPS = ["email", "firstname", "lastname", "createdate", "hubspot_owner_id", "hubspot_owner_assigneddate",
         "recent_conversion_event_name", "recent_conversion_date", "first_conversion_event_name",
         "num_conversion_events", "cursos_piura__udn_udep_", "programas_piura__udn_udep_", "cursos_piura",
         "mensaje", "message", "medio_de_contacto__udn_udep_", "nivel_de_estudios__udn_udep_",
         "hs_analytics_source", "hs_analytics_first_url", "lifecyclestage"]

def norm(s):
    return " ".join((s or "").lower().split())

pend = [i for i in envios["instancias"] if i.get("correo") and i.get("R3_envio") and not i.get("dry_run")]
print(f"instancias enviadas a verificar: {len(pend)}")
ok_h1 = ok_h2 = ok_h5 = 0
for i in pend:
    r = hs.api("POST", "/crm/v3/objects/contacts/search", json={
        "filterGroups": [{"filters": [{"propertyName": "email", "operator": "EQ", "value": i["correo"]}]}],
        "properties": PROPS, "limit": 1})
    if r.status_code != 200 or not r.json().get("results"):
        i.update({"H1_contacto": False, "hs_object_id": None, "H2_atribucion": None, "H5_disparo": None,
                  "form_id_registrado": None, "H3_programa_real": None})
        print(f"  SIN CONTACTO  {i['slug'][:50]}/{i['instancia']}")
        continue
    c = r.json()["results"][0]
    (RAW / f"{c['id']}.json").write_text(json.dumps(c, ensure_ascii=False, indent=2), encoding="utf-8")
    p = c.get("properties", {})
    esperado = forms.get(i.get("form_id_esperado") or "", {}).get("nombre") or next(
        (f["nombre"] for f in forms.values() if f["slug"] == i["slug"]), None)
    conv = p.get("recent_conversion_event_name") or p.get("first_conversion_event_name")
    i["H1_contacto"] = True
    i["hs_object_id"] = c["id"]
    i["form_id_registrado"] = conv                      # HubSpot registra el nombre del formulario
    i["H2_atribucion"] = (norm(conv) == norm(esperado)) if conv and esperado else None
    i["H3_programa_real"] = p.get("cursos_piura__udn_udep_") or p.get("programas_piura__udn_udep_") or p.get("cursos_piura")
    dueno = str(p.get("hubspot_owner_id") or "")
    i["H5_disparo"] = bool(dueno)
    i["propietario"] = dueno or None
    i["propietario_email"] = PROPIETARIOS.get(dueno)
    i["fuga_a_ejecutivo_real"] = bool(dueno) and dueno not in NUESTROS
    i["estatus_de_gestion"] = p.get("estatus_de_gestion")
    i["mensaje_llego_a"] = "mensaje" if p.get("mensaje") else ("message" if p.get("message") else None)
    i["verificado_en"] = hs.ahora()
    ok_h1 += 1; ok_h2 += bool(i["H2_atribucion"]); ok_h5 += bool(i["H5_disparo"])
    alerta = "  <-- FUGA: propietario ajeno a 5minutos" if i["fuga_a_ejecutivo_real"] else ""
    print(f"  {i['slug'][:42]:42}/{i['instancia']:6} H1 ok · H2 {str(i['H2_atribucion']):5} · "
          f"H5 {str(i['H5_disparo']):5} · duenio {i.get('propietario_email') or '-'} · "
          f"programa='{i['H3_programa_real']}'{alerta}")
    time.sleep(0.2)

hs.guardar("30_envios.json", envios)
fugas = [f"{i['slug']}/{i['instancia']} -> {i.get('propietario_email')}" for i in pend if i.get("fuga_a_ejecutivo_real")]
print(f"\nH1 contacto creado: {ok_h1}/{len(pend)} · H2 atribuido al formulario correcto: {ok_h2}/{len(pend)} · H5 con propietario asignado: {ok_h5}/{len(pend)}")
print("Nota: H5 usa el propietario asignado como efecto observable del Activador. Si un contacto no tiene")
print("propietario a los pocos minutos del envio, el Activador no se ejecuto o el workflow de asignacion no lo tomo.")
if fugas:
    print(f"\n*** ATENCION: {len(fugas)} contacto(s) de prueba quedaron asignados a un propietario ajeno a 5minutos.")
    print("*** Detene la pasada y avisa: son leads falsos cayendo sobre ejecutivos reales.")
    for f in fugas[:20]:
        print("   ", f)
else:
    print("Sin fugas: ningun contacto de prueba quedo asignado a un ejecutivo ajeno a 5minutos.")
