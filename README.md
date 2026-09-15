# Auditoría de formularios · UDEP Online

Paquete autónomo para Claude Code. Audita los 40 formularios de producto de udeponline.pe sobre el
portal HubSpot 6925781: envío real, atribución, Activador, marca, campos y reCAPTCHA.

## Puesta en marcha

```bash
cd auditoria-formularios-udep
pip install -r requirements.txt
python3 -m playwright install chromium

# abrir .env y pegar el token de HubSpot en HUBSPOT_TOKEN
```

**El token** sale de una private app del portal 6925781 con estos scopes: `forms`,
`crm.objects.contacts.read`, `crm.objects.contacts.write` (solo para la limpieza final) y
`automation`.

Después, en Claude Code:

```
/model claude-fable-5-1
```

y esfuerzo **medio**. Los agentes ya lo declaran, pero la sesión principal manda sobre el modo de
permisos, así que conviene que coincida.

**Dependencia de skill.** El agente `redactor-informe` precarga `consulting-deliverable-system`.
Si no la tenés instalada, el campo se ignora sin avisar y el informe de la ronda 6 sale sin la
estructura de entregable. Comprobalo con `/skills` antes de arrancar.

Luego pegá el prompt de arranque que te pasó Santiago. No hace falta nada más.

## Sobre el conector MCP de HubSpot

Si lo tenés conectado, **este proyecto no lo usa y lo deniega a propósito**. Toda consulta al portal
va por los scripts de `tools/`, que son los que dejan la evidencia en disco. Una consulta por MCP
devuelve el dato al contexto y no deja archivo, y sin archivo el verificador de la ronda 4 falla.
No hace falta que lo desconectes: la regla `deny` lo bloquea solo.

## Qué hay adentro

```
CLAUDE.md                 reglas duras y mapa de rondas
LOOP.md                   diseño del bucle y guardas de parada
.claude/settings.json     permisos, hooks
.claude/agents/           los 9 agentes, uno por rol
.claude/hooks/            bloqueo de secretos y de escrituras no contempladas
tools/                    los scripts que producen la evidencia
input/paginas.json        las 40 páginas con su formId, medido el 15-sep-2026
input/requirements.md     el requerimiento aprobado — fuente de verdad
output/                   todo lo que produce la corrida
```

## Arrancar en seco

`.env.example` trae `DRY_RUN=1`. Con eso el flujo recorre las páginas y saca capturas pero **no
envía**. Sirve para comprobar que Playwright y los selectores andan. Una corrida en seco **no cierra
la auditoría**: el verificador la marca como fallida a propósito.

Para la pasada real: `DRY_RUN=0`.

## Antes de la pasada real

Avisá al equipo comercial de UDEP. Los 80 envíos crean contactos reales y, si los Activadores
funcionan —que es justo lo que se quiere comprobar—, esos contactos se asignan a ejecutivos y
entran en la maquinaria de SLA. Van identificados con el patrón `qa+…@5minutos.io` y se borran al
final, pero mientras tanto están a la vista.

## Al terminar

`output/informe_formularios_udep.md` y `output/registro_pruebas.csv`. El informe es para Vicente;
el registro es lo que pidió literalmente.

La limpieza de los contactos de prueba es el único paso que pide aprobación humana:

```bash
python3 tools/limpiar_pruebas.py            # lista lo que borraría
python3 tools/limpiar_pruebas.py --ejecutar # borra
```
