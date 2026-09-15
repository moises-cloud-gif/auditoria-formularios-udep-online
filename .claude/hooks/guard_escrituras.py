#!/usr/bin/env python3
"""Impide escrituras al CRM que no esten explicitamente contempladas.

Regla: la auditoria es de solo lectura sobre HubSpot, salvo dos excepciones.
  1. El envio de formularios, que va por el endpoint publico de forms y es
     exactamente lo que hace un visitante.
  2. La limpieza final de contactos de prueba, que exige --ejecutar y pasa por 'ask'.
Cualquier otro PATCH, PUT, POST o DELETE contra api.hubapi.com se bloquea aca,
no en el CLAUDE.md, porque el CLAUDE.md se puede ignorar y un hook no.
"""
import json, sys, re

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

cmd = str((data.get("tool_input", {}) or {}).get("command", ""))

# Nadie llama a la API a mano: para eso estan los scripts de tools/.
if re.search(r"api\.hubapi\.com", cmd, re.I) and not re.search(r"tools/[a-z_]+\.py", cmd):
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Llamada directa a la API de HubSpot. Usa los scripts de tools/, que llevan guarda de portal y registro de evidencia."
    }}))
    sys.exit(0)

# La limpieza real no corre sin que un humano la apruebe.
if "limpiar_pruebas.py" in cmd and "--ejecutar" in cmd:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "ask",
        "permissionDecisionReason": "Borrado de contactos de prueba en el portal productivo. Lo aprueba Moises, no el agente. No existe bandera para saltear esto."
    }}))
    sys.exit(0)

sys.exit(0)
