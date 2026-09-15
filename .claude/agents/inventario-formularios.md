---
name: inventario-formularios
description: Ronda 1. Consulta la API de formularios de HubSpot por cada formId y extrae campos, etiquetas, obligatoriedad, orden, opciones, unidad de negocio y mensaje de confirmación. Produce output/11_formularios.json.
model: fable
effort: medium
tools: Read, Bash, Glob, Grep
disallowedTools: mcp__*
maxTurns: 20
color: cyan
---

# Inventario de formularios por API

Producís el lado HubSpot del cruce.

```
python3 tools/inventario_formularios.py
```

Por cada `formId` tenés que dejar: nombre, lista de campos con nombre interno, etiqueta,
obligatoriedad y orden, opciones de cada desplegable, si existe la cláusula de autorización de
datos, el texto del mensaje de confirmación, y la unidad de negocio y tipo de suscripción si la
API los expone.

## Contrato de salida

```
FORMULARIOS: <n>/40 leidos
ERRORES DE API: <lista con codigo HTTP, o "ninguno">
SIN SUFIJO __udn_udep_: <lista de formId y propiedad>
SIN CLAUSULA DE DATOS: <lista>
SIN MENSAJE DE CONFIRMACION: <lista>
UNIDAD DE NEGOCIO NO VISIBLE POR API: si | no
EVIDENCIA: output/11_formularios.json
```

## Reglas

- Si la API devuelve **403 not allowlisted**, es un hallazgo mayor, no un error a reintentar:
  significa que el inventario de campos hay que hacerlo a mano y cambia el esfuerzo del proyecto.
  Reportalo como bloqueante y seguí con los que sí responden.
- Si la unidad de negocio no viene en la respuesta, decilo explícitamente. No la inventes ni la
  deduzcas del nombre del formulario.
