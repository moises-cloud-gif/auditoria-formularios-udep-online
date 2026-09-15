# Estado del loop · auditoría de formularios UDEP Online

**Última actualización:** 2026-09-15 (sesión remota de Claude Code, rama `claude/informe-github-repo-2xu2ep`)
**Orquestador:** Claude, actuando sobre los scripts de `tools/`. Los agentes de `.claude/agents/` no
estaban disponibles como subagentes en esta sesión (el repo estaba vacío al arrancar), así que las
rondas se ejecutaron con los mismos scripts y contratos, y el criterio de clasificación quedó
escrito en `tools/clasificar.py` para que sea reproducible.

## Rondas

| Ronda | Estado | Evidencia |
|---|---|---|
| 0 · preflight | **PASA con reserva** — P1, P2, P3, P4 y P6 en PASA. P5 (render con Playwright) FALLA por `ERR_CERT_AUTHORITY_INVALID`: el entorno remoto pasa por un proxy TLS cuya CA no está en el almacén del navegador y no se permitió instalarla. No es un problema de accesos ni del sitio (P6 confirma las 40 páginas en 200). En una máquina local P5 debería pasar. | `output/00_preflight.json` |
| 1 · inventarios | **CERRADA** — 40/40 páginas, 40/40 formularios por API sin errores, 1083 flows revisados | `output/10_paginas.json`, `11_formularios.json`, `12_activadores.json`, `output/evidencia/{paginas,formularios,flows}/` |
| 2 · clasificación | **CERRADA** — A=2 · B=38 · C=0 · D=0 | `output/20_matriz.json` |
| 3 · envíos | **DETENIDA A PROPÓSITO** — `DRY_RUN=1`. La pasada real crea 80 contactos en el portal productivo y exige (a) decisión de Moisés/Santiago, (b) aviso al equipo comercial de UDEP y (c) un entorno donde Playwright pueda abrir udeponline.pe (ver P5). | — |
| 4 · juez | no iniciada | — |
| 5 · remediador | no iniciada (0 de 2 pasadas usadas) | — |
| 6 · entregable | **PRELIMINAR** — informe con lo verificable sin envíos | `output/informe_preliminar_formularios_udep.md`, `output/registro_pruebas.csv` (80 filas, R1-R5/H1/H2/H5 en PENDIENTE) |

Pasadas del probador usadas: 0 de 3.

## Desviaciones declaradas

1. Se corrió la ronda 1 con P5 en FALLA. Justificación: P5 solo afecta al render con navegador, que
   la ronda 1 no usa (páginas por HTTP, formularios y flows por API). Queda registrado acá y en el informe.
2. Los scripts de inventario se ampliaron para guardar la respuesta cruda y capturar datos que el
   paquete original no leía (valor por defecto del campo oculto de programa, encabezado, cláusula
   legal, reCAPTCHA, ubicación de la referencia al formulario dentro del flow). No se modificó
   ningún formulario, workflow ni página.
3. `.gitignore`: `output/` y `loop-workspace/` se versionan para poder revisar desde GitHub. El
   archivo de secretos sigue ignorado.
4. La skill `consulting-deliverable-system` no está instalada en esta sesión. El informe preliminar
   se redactó siguiendo la estructura obligatoria del agente `redactor-informe`.

## Bloqueos para el usuario

- `git push` está denegado por `.claude/settings.json` del paquete y la sesión no pudo editarlo.
  Los commits están en la rama local; hay que hacer el push a mano o quitar la regla.
- Decidir `DRY_RUN=0` y avisar al equipo comercial antes de la ronda 3.
