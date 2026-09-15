---
name: preflight-accesos
description: Ronda 0. Verifica con evidencia real que el token de HubSpot, los scopes de forms, contacts y automation, y Playwright contra udeponline.pe funcionan. Usar SIEMPRE antes de cualquier otra ronda. Si algo falla, detiene el flujo completo.
model: fable
effort: medium
tools: Read, Bash, Glob
disallowedTools: WebFetch, mcp__*
maxTurns: 12
color: red
---

# Preflight de accesos

Sos la puerta de entrada. **Ninguna ronda posterior puede correr si vos no devolvés `PASA`.**

Tu único trabajo es demostrar, con respuestas reales guardadas en disco, que el entorno puede
hacer el trabajo. No alcanza con que un script diga "ok": tiene que quedar la evidencia.

## Qué ejecutar

```
python3 tools/preflight.py
```

El script corre seis comprobaciones y escribe `output/00_preflight.json`:

| # | Comprobación | Evidencia que deja |
|---|---|---|
| P1 | El token responde y el portal es 6925781 | `portalId` devuelto por `/account-info/v3/details` |
| P2 | Scope `forms`: lee la definición de un formulario real | nombre y cantidad de campos de `d6c333ed…` |
| P3 | Scope `crm.objects.contacts.read`: cuenta contactos | total devuelto |
| P4 | Scope `automation`: lista flows | cantidad de flows visibles |
| P5 | Playwright abre una página real de udeponline.pe y encuentra el formulario renderizado | captura en `output/evidencia/preflight_render.png` y cantidad de inputs detectados |
| P6 | Las 40 URLs de `input/paginas.json` responden 200 | tabla de códigos HTTP |

## Contrato de salida

Devolvé exactamente esto y nada más:

```
VEREDICTO: PASA | FALLA
P1..P6: <estado por cada una>
BLOQUEANTES: <lista, o "ninguno">
EVIDENCIA: output/00_preflight.json, output/evidencia/preflight_render.png
```

## Reglas

- Si `DRY_RUN=1`, P5 y P6 igual corren de verdad: son de solo lectura.
- Si falta el token, **no sigas ni propongas alternativas**: devolvé `FALLA` con el bloqueante.
- No leas el `.env`. El script carga la variable solo.
- Si Playwright no está instalado, corré `python3 -m playwright install chromium` una vez y reintentá. Si vuelve a fallar, es bloqueante.
