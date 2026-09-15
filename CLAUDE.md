# Auditoría de formularios · UDEP Online

Verificar por envío real que los 40 formularios de producto de udeponline.pe capturan, atribuyen
y enrutan correctamente; normalizar los que estén mal; y confirmar desde HubSpot lo que Vicente Ham
no puede ver con su token.

El requerimiento completo, con los criterios de aceptación, está en `input/requirements.md`.
**Es la fuente de verdad. Si algo de este archivo lo contradice, gana el requerimiento.**

## Entorno

- **Portal HubSpot:** 6925781 — compartido entre UANDES Online y UDEP Online. Solo se toca lo de UDEP.
- **Sitio:** udeponline.pe, WordPress + Elementor, lo gestiona Vicente (externo).
- **Modelo:** Claude Fable 5.1, esfuerzo medio. Los agentes lo declaran; la sesión también debe estarlo.
- **Insumo sembrado:** `input/paginas.json` trae las 40 páginas con su `formId`, medido el 15-sep-2026.
  Se reconfirma contra el sitio vivo, no se copia.

## Reglas duras

1. **Nada corre si el preflight no devuelve PASA.** Sin token, sin scopes o sin Playwright no hay
   auditoría: hay texto sobre un sistema que no se vio.
2. **Ninguna ronda se cierra sin evidencia en disco.** Captura de pantalla e `hs_object_id` real por
   instancia. Una fila sin las dos cosas cuenta como fallo, no como pendiente.
3. **Solo lectura sobre HubSpot**, con dos excepciones: el envío por el endpoint público de
   formularios, y la limpieza final, que exige aprobación de Moisés.
4. **Nadie llama a la API a mano y nadie usa el MCP de HubSpot.** Todo pasa por los scripts de
   `tools/`, que llevan guarda de portal, backoff y guardado de la respuesta cruda. El conector MCP
   está denegado en `settings.json` y en cada agente. No es una preferencia de estilo: una consulta
   por MCP devuelve el dato en el contexto y **no deja archivo de evidencia**, así que el
   verificador de la ronda 4 no la ve y la ronda falla aunque el trabajo se haya hecho. Si el MCP
   está conectado en tu sesión, igual no se usa acá.
5. **El `.env` no se lee.** El token lo cargan los scripts con dotenv. Hay un hook que lo bloquea.
6. **No se modifica ningún formulario ni workflow en esta corrida.** La auditoría diagnostica; la
   corrección es una tarea posterior con su propia aprobación.
7. **`DRY_RUN=1` no cierra ninguna ronda.** Sirve para probar el script.

## Las rondas

Detalle y guardas de parada en `LOOP.md`.

| Ronda | Agente | Sale con |
|---|---|---|
| 0 | `preflight-accesos` | `output/00_preflight.json` · **gate duro** |
| 1 | `inventario-paginas` · `inventario-formularios` · `inventario-activadores` (en paralelo) | `10_`, `11_`, `12_` |
| 2 | `clasificador-casos` | `20_matriz.json` con el reparto A/B/C/D |
| 3 | `probador-envios` | `30_envios.json` + capturas |
| 4 | `juez-evidencia` | veredicto PASA o REVISAR |
| 5 | `remediador` | solo los huecos del juez · **máximo 2 pasadas** |
| 6 | `redactor-informe` | informe + registro CSV |

El bucle es 3 → 4 → 5 → 4. Tope absoluto: **tres pasadas del probador**. Si al terminar la tercera
el juez sigue en REVISAR, el loop se cierra igual y se escala a Moisés con la lista de huecos
abiertos. Un loop que no puede terminar mal no es un loop, es una ceremonia.

## Riesgos aceptados, declarados a propósito

**`defaultMode` está en `acceptEdits`, no en `default`.** Para un portal de cliente en vivo la
metodología pide `default`, que pregunta antes de cada escritura. Acá se relajó porque el
requerimiento es que la pasada corra sola. Lo que compensa la diferencia no es la confianza sino
el alcance: sobre HubSpot esto es **solo lectura**, salvo el envío público de formularios y la
limpieza final, y las dos excepciones están cerradas con hooks que no se pueden ignorar. Ninguna
escritura al CRM pasa por `acceptEdits`.

**Los 80 envíos crean contactos reales que se asignan a ejecutivos reales.** Es el costo de
verificar de verdad que el Activador dispara. Se mitiga con el patrón `qa+…@5minutos.io`, el aviso
previo al equipo de UDEP y la limpieza al cierre. No se mitiga pausando los Activadores: eso haría
inverificable justamente lo que se quiere probar.

**El agente `redactor-informe` precarga la skill `consulting-deliverable-system`.** Si esa skill no
está instalada en el entorno, el campo se ignora en silencio y el informe sale sin la estructura de
entregable. Verificalo antes de la ronda 6.

## Lo que decide Moisés y no el agente

- Aprobar la limpieza de los contactos de prueba.
- Si el reCAPTCHA resulta ser de portal: informar a Rocío antes de tocarlo, porque alcanza a UANDES.
- Qué se hace con cada caso B, C y D. La auditoría clasifica; no corrige.
- La fecha que se le compromete a Vicente.

## Primer comando

```
python3 tools/preflight.py
```
