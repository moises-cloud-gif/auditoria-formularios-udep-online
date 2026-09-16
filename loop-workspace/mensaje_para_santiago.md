# Para Santiago · auditoría de formularios UDEP Online · 15-sep-2026

## Dónde estamos

Terminamos la parte de diagnóstico sin tocar nada: leímos los 40 formularios, las 40 páginas y los
flujos de asignación del portal. Falta la prueba de envío real (80 envíos), que crea contactos de
verdad en el HubSpot productivo y por eso está frenada hasta tener las decisiones de abajo.

## Qué encontramos, en corto

1. **Solo 2 de 40 formularios están bien.** Los otros 38 se corrigen desde HubSpot, del lado de
   5minutos. **Vicente no tiene que repuntar ninguna página.**
2. **37 formularios atribuyen el lead al programa equivocado.** El campo oculto que dice "qué curso
   pidió el lead" trae el mismo valor copiado en todos: "Gestión del Talento" en los cursos,
   "Marketing Digital y Ecommerce" en programas y diplomados. El lead se asigna igual, pero llega al
   ejecutivo con el programa mal y los reportes por curso están mal desde el 15-sep. Todo indica que
   lo causó la normalización masiva que hizo Vicente ese día.
3. **El formulario nuevo de Analítica Digital & Growth Marketing no está conectado a ningún
   Activador.** Los leads entran y no se le asignan a nadie. Además no existe la opción de ese curso
   en la propiedad de programa.
4. **Los 4 formularios que Vicente no puede editar** sí los podemos leer y editar nosotros. Les falta
   cláusula de datos, mensaje de gracias, encabezado y valor de programa.
5. **reCAPTCHA:** está activado en los 40. Si es clave de prueba, es del portal completo y alcanza a
   UANDES. Se confirma solo viendo el formulario en pantalla (prueba real).

## Lo que necesitamos del lado de UANDES / UDEP

**De Santiago (aprobaciones):**
- OK para correr la prueba real de 80 envíos con los Activadores encendidos. Sin eso no se puede
  cerrar la auditoría ni verificar que la asignación funcione.
- OK para editar los 38 formularios en HubSpot (caso B), en este orden: los 2 cursos nuevos,
  después los 4 de junio, después los 32 restantes.
- OK para conectar el formulario de Analítica Digital al Activador de Cursos y crear la opción del
  curso en la propiedad de programa. Son cambios en HubSpot que la auditoría no hizo.
- Fecha para comprometerle a Vicente. Ahora sí se puede fijar: ya sabemos que son 38 ediciones
  nuestras y 0 repunteos de él.
- Decidir si la migración de datos históricos y la re-atribución de los leads de Analítica Digital
  se cotizan aparte o se descartan.

**Del equipo comercial de UDEP:**
- Aviso previo de la ventana horaria de la prueba real, para que ignoren los 80 leads de prueba
  (todos empiezan con `qa+` y dicen "PRUEBA QA 5MINUTOS - NO GESTIONAR").
- Confirmar quién administra los Activadores, para validar dos asignaciones de clúster que no
  cuadran por nombre: *Diplomado en Marketing Digital y Ecommerce* (entra por Marketing Digital,
  no por Diplomados) y *PDE en Gestión del Cambio y Negociación de Conflictos* (entra por
  Emprendimiento e Innovación).

**De Vicente:**
- Que nos diga qué valor mandó su script al campo oculto de programa el 15-sep, para confirmar la
  causa del punto 2.
- Limpiar la página de *Liderazgo y Negociación de Conflictos*: tiene 8 bloques de formulario en
  vez de 2, seis con marcadores sin resolver.
- Coordinar el título "¿QUIERES MÁS INFORMACIÓN?": hoy está en la página de WordPress y también
  dentro de 36 formularios, así que probablemente se ve dos veces. Cuando corrijamos los 4
  restantes va a pasar en esos también.
- Despublicar o revisar la página `programas-de-especializacion-dev/`, que sigue publicada.

**De Rocío (UANDES):**
- Solo si el reCAPTCHA se confirma como clave de prueba: avisarle antes de tocarlo, porque el
  cambio alcanza a los formularios de UANDES Online.

## Cruce contra el canon Piura (16-sep)

Hecho, con el token cargado: las 80 instancias resueltas por API y cruzadas con la planilla.
**0 discrepancias reales.** Los 40 identificadores del sitio son los correctos; las 6 diferencias
con la planilla son errores de la planilla (los nombres cruzados de Liderazgo/Gestión del Talento y
Negociación, y Digital Business Model, que tiene dos formularios activos para el mismo curso).
Dos páginas no tienen fila en la planilla. Tabla para Vicente: `output/cruce_canon_vicente.csv`.

## Lo que se hizo con tu checklist (16-sep), sin navegador

- **Seguridad P0 (ClickFix):** 0 indicadores en el HTML de las 40 páginas y en los 38 scripts propios del sitio; todos los dominios de scripts son reconocidos. Límite: es lo que el servidor entrega; la confirmación final es con navegador en la ronda 3.
- **Título 7 vs 36:** no se contradicen. Agosto contó 7 en pantalla, antes de la normalización, y 4 de esos 7 son los formularios de junio (sin encabezado en HubSpot: era marcado de WordPress). Hoy 36 formularios traen encabezado propio desde el 15-sep y las 36 páginas también lo traen en WordPress, sin CSS que oculte ninguno: riesgo estructural en 36. El conteo en pantalla queda para la ronda 3, y ese es el número para Vicente.
- **Embed nuevo:** 39 páginas usan la incrustación plana; solo Liderazgo y Negociación usa el bloque nuevo (en sus 6 copias rotas). No aparece un grupo de "3 cursos con embed nuevo" en el HTML actual.
- **Agosto:** `negocios-innovadores/` ya redirige (301) a la página real; los 6 diplomados están publicados con formulario (instructivo F cerrado); la página de test da 404; la URL "enfelicidad" era un error de la planilla. Si el "diplomado caído" es otra URL, decime cuál.
- **Planilla canon:** propuesta corregida con 17 cambios marcados en amarillo y hoja de cambios, sin pisar la original (`output/canon_piura_propuesta_corregida.xlsx`). Quién la mantiene: decisión pendiente.
- **Hipótesis del 15-sep:** el informe ya la trata como hipótesis a confirmar con Vicente, no como hecho.
- **Borrador a Rocío/comercial:** retenido hasta la ronda 3, como pediste. La versión matizada está abajo.

## Borrador matizado para UANDES / UDEP (NO ENVIAR hasta cerrar la ronda 3)

> Avance de la auditoría de formularios de UDEP Online. Revisamos los 40 formularios, las 40 páginas y los flujos de asignación.
> Por identificador, los 40 formularios incrustados son los correctos: ninguna página apunta al formulario de otro programa. Pero 38 de los 40 formularios tienen algo que corregir por dentro, y lo más importante es que 37 guardan el lead con un programa de interés equivocado (o ninguno). El lead se asigna, pero llega mal etiquetado. Eso lo corregimos nosotros en HubSpot.
> Del lado web sí hay trabajo para Vicente: limpiar los 8 bloques de formulario de Liderazgo y Negociación, resolver el título que aparece dentro del formulario y en la página, y revisar la página de prueba que sigue publicada.
> Para cerrar necesitamos: (equipo comercial) ventana para la prueba real de 80 envíos con contactos "qa+" que no hay que gestionar; (Vicente) qué valor envió su script del 15-sep al campo de programa; (Rocío) solo si el reCAPTCHA resulta ser clave de prueba, avisarte antes de tocarlo porque alcanza a UANDES.

## Evidencia

Informe preliminar y registro de 80 filas en el repositorio
`moises-cloud-gif/auditoria-formularios-udep-online`, carpeta `output/`.
