# Pedido a Roman · cómo desviar los contactos de prueba sin romper la auditoría

**Fecha:** 17-sep-2026 · **Decisión:** Moisés y Pedro · los contactos de prueba se asignan a
nosotros, no se excluyen del circuito.

## Lo que hay hoy

El 17-sep a las 13:19 se agregó una **meta** al flujo `1631981736` (*0451. Definición Nivel de
Estudios Perú*) que expulsa a todo contacto con dominio `5minutos.io`.

Cadena real: formulario → Activador → `0451` → `1631990199` (*0452. LEADS-Asignación de leads a
equipo Piura*).

Con esa meta los contactos de prueba salen en `0451` y nunca llegan a `0452`, así que no reciben
propietario, ni tarea, ni estatus de gestión. Eso cumple el pedido de Pedro. Evidencia:
`output/44_cadena_workflows.json`.

## El problema

La auditoría mide **H5 = "el Activador se ejecutó para este contacto"**, y el único efecto
observable es que quede asignado un propietario. Con la meta puesta, ningún contacto de prueba va a
tener propietario, y el informe diría que los Activadores no disparan. Es lo contrario de la
verdad, y es la pregunta principal del proyecto.

## Lo que pedimos

Es la segunda opción que propuso Pedro: *"que se asignen a uno de ustedes"*.

1. **Quitar la meta del flujo `0451`** que filtra por `hs_email_domain` = `5minutos.io`.
2. **En el flujo `0452`, agregar una rama al principio** para contactos cuyo correo contenga
   `qa+` y termine en `@5minutos.io`. Esa rama debe:
   - asignar `hubspot_owner_id` = **`82923019`** (Moisés Camargo, `moises@5minutos.io`);
   - **no** crear la tarea "Contactar dentro del día";
   - **no** escribir `estatus_de_gestion`;
   - **no** inscribir en los flujos siguientes (`1631989399`, `1741893789`).
3. El resto de los contactos sigue por la rama normal, sin cambios.

Con eso: el Activador se ejecuta y queda demostrado, ningún ejecutivo real recibe nada, no se crea
ninguna tarea y no se tocan propiedades MQL.

Nota: el filtro debe ser por el patrón `qa+`, no por el dominio entero. Si se filtra todo
`5minutos.io`, cualquier lead real nuestro queda fuera del circuito.

## Al terminar la pasada

**Revertir el punto 2**, es decir quitar la rama de `0452`. Mientras esté puesta, cualquier contacto
con el patrón `qa+@5minutos.io` queda desviado. Responsable de revertir y fecha: a definir.

## Para declarar en el informe

La regla 6 de la auditoría dice que no se modifica ningún workflow durante la corrida, y se
modificó uno de producción. Queda declarado como desviación aceptada: la pasada mide el portal con
esta rama activa, no el portal en su estado normal. Lo que **no** cambia es lo que se quiere
comprobar, porque la rama solo altera a quién se asigna, no si el Activador dispara.
