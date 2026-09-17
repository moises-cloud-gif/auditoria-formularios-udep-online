# Pedido a Roman · versión 2 · ver el ruteo sin tocar a nadie

**17-sep-2026.** Decidido con Pedro: queremos saber a qué equipo habría ido cada lead. Sin eso el
informe no responde la pregunta del cliente.

## Lo que ya está bien y no hay que tocar

Roman modificó cuatro workflows hoy entre las 13:18 y las 13:21, todos con una meta que excluye el
dominio `5minutos.io`: el `0451` y los tres de MQL. **El pedido de Pedro sobre MQL está resuelto y
verificado** (`output/46_donde_se_marca_mql.json`, 1093 flows revisados, y
`output/47_mql_veredicto.json`). Los tres workflows de MQL además se inscriben por equipo asignado,
así que hay doble protección. **Nada de eso hay que cambiar.**

## Lo único que queda abierto

La meta del `0451` expulsa a los contactos de prueba **antes** de que se clasifiquen. Resultado: no
sabemos a qué equipo, a qué facultad ni a qué país los habría mandado el sistema. Y eso es
justamente lo que interesa, porque el hallazgo principal de la auditoría es que **37 formularios
mandan el programa equivocado**, y el `0452` usa el programa para elegir facultad y equipo.

## Lo que pedimos · opción mínima (un solo cambio)

**Mover la meta del `0451` al `0452`.**

- Quitar la meta de `hs_email_domain` = `5minutos.io` del flujo `1631981736` (*0451*).
- Ponerla en el flujo `1631990199` (*0452*), con el mismo criterio.

Con eso los contactos de prueba **sí** pasan por el `0451`, que es donde se decide país y equipo, y
salen justo antes del `0452`, que es donde se asigna el ejecutivo, se crea la tarea, se manda el
correo automático y se genera el ticket de SLA.

Qué ganamos: el equipo asignado, el país y el programa que quedó registrado en cada lead.
Qué seguimos evitando: ejecutivo asignado, tarea, correo al contacto, ticket de SLA y MQL.

## Opción ideal (un paso más, opcional)

Si además querés que quede demostrado que la cadena llega hasta el `0452`, en vez de una meta poné
una rama al principio del `0452` para los correos que contengan `qa+` y terminen en
`@5minutos.io`, que asigne `hubspot_owner_id` = **`82923019`** (Moisés) y no haga nada más: ni
tarea, ni estatus de gestión, ni inscripción en `1631989399` (correos) ni en `1741893789` (SLA).

Con eso vemos también la facultad asignada.

## Al terminar la pasada

Revertir el cambio. Mientras esté puesto, cualquier contacto con dominio `5minutos.io` queda fuera
del circuito comercial. Definir quién revierte y cuándo.

## Nota para el informe

La regla 6 de la auditoría dice que no se modifica ningún workflow durante la corrida, y se
modificaron cinco de producción. Queda declarado como desviación aceptada, acordada con Pedro y
aprobada por Santiago: la pasada mide el portal con estas exclusiones activas.
