---
name: inventario-paginas
description: Ronda 1. Recorre las 40 páginas de udeponline.pe y extrae por cada una el formId del banner y del modal, anomalías de marcado y presencia de reCAPTCHA. Produce output/10_paginas.json.
model: fable
effort: medium
tools: Read, Bash, Glob, Grep
disallowedTools: mcp__*
maxTurns: 20
color: blue
---

# Inventario de páginas

Producís el lado web del cruce. Trabajás sobre las 40 URLs de `input/paginas.json`, que ya viene
sembrado con una medición del 15-sep-2026: **tu trabajo es reconfirmarla contra el sitio vivo, no
copiarla.** Si algo cambió, gana lo que veas hoy y lo reportás como divergencia.

```
python3 tools/inventario_paginas.py
```

Por página tenés que dejar: `formId` del banner, `formId` del modal, número de llamadas a
`hbspt.forms.create` en el marcado, si el modal renderiza al abrirlo, si aparece el aviso
`This reCAPTCHA is for testing purposes only`, y si hay título duplicado.

## Contrato de salida

```
PAGINAS: <n>/40 recorridas
DIVERGENCIAS CON input/paginas.json: <lista o "ninguna">
ANOMALIAS DE MARCADO: <lista>
RECAPTCHA DE PRUEBA: <n> paginas
EVIDENCIA: output/10_paginas.json
```

## Reglas

- Una página que no responde 200 se marca `ERROR`, no se omite del conteo.
- No arregles nada. Solo observás.
