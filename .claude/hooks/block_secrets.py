#!/usr/bin/env python3
"""Bloquea la lectura del .env por cualquier via, incluido Bash.

El token de HubSpot lo leen los scripts de tools/ con python-dotenv.
El agente no necesita verlo nunca, y si lo ve queda en el contexto.
"""
import json, sys, re

PATRONES = [r"\.env\b", r"secrets/", r"credentials", r"\.pem$", r"id_rsa", r"HUBSPOT_TOKEN"]

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

ti = data.get("tool_input", {}) or {}
objetivo = " ".join(str(ti.get(k, "")) for k in ("file_path", "command", "content", "new_string"))

# Los scripts pueden nombrar la variable; lo que se bloquea es imprimirla o leer el archivo.
# .env.example es publico y no lleva secretos: se excluye a proposito.
objetivo_limpio = objetivo.replace(".env.example", "")

sospechoso = (
    any(re.search(p, objetivo_limpio, re.I) for p in PATRONES)
    and not re.search(r"dotenv|load_dotenv", objetivo_limpio, re.I)
)

if sospechoso:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "Lectura de secretos bloqueada. El token lo cargan los scripts con dotenv; el agente no lo ve."
    }}))
    sys.exit(0)

sys.exit(0)
