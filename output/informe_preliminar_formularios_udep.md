# Auditoría de formularios · UDEP Online — informe preliminar (rondas 0 a 2)

**Fecha:** 15 de septiembre de 2026 · actualizado 16-sep con el cruce contra el canon Piura, seguridad, título y reconciliación con agosto · **Portal HubSpot:** 6925781 · **Sitio:** udeponline.pe
**Estado:** PRELIMINAR. Cubre lo verificable sin enviar formularios: definición de los 40
formularios por API, marcado de las 40 páginas y los workflows Activador del portal. La prueba de
envío real (80 instancias) no se ejecutó todavía; ver "Lo que no se pudo verificar".

---

## Respuesta

**De los 40 formularios, solo 2 capturan, atribuyen y enrutan bien según lo que se puede ver sin
enviar. Los otros 38 tienen al menos un defecto crítico.** El más extendido no lo reportó nadie:
**37 formularios atribuyen el lead a un programa distinto del de su página o a ninguno**, porque el
campo oculto que lleva el nombre del programa trae el mismo valor en todos (registro
`20_matriz.json`, columna `H3`). Además, el formulario nuevo de *Analítica Digital & Growth
Marketing* **no está conectado a ningún Activador**: sus leads entran al CRM y no se asignan a
nadie (`12_activadores.json`, `7a38b319`).

Los dos que están bien: *Curso Gestión del Talento* (`d6c333ed`, que es la plantilla) y *PDE en
Marketing Digital y E-commerce* (`cd64140f`).

| Verificación | Resultado sobre 40 | Evidencia |
|---|---|---|
| Programa correcto en el campo oculto (H3) | **2 bien · 33 envían otro programa · 4 sin valor · 1 sin opción disponible** | `20_matriz.json` |
| Un Activador por formulario (H4) | **39 con exactamente uno · 1 sin ninguno** · 2 a revisar por clúster | `12_activadores.json` |
| Definición igual a la plantilla (H7) | 36 iguales (24 con la variante de programas) · **4 con desvíos** | `11_formularios.json` |
| Cláusula de autorización de datos | 36 sí · **4 no** | `11_formularios.json` |
| Mensaje de confirmación "Gracias, te contactaremos a la brevedad." | 36 sí · **4 vacío** | `11_formularios.json` |
| Unidad de negocio y tipo de suscripción (H6) | **no lo expone la API** · pendiente en la interfaz | `11_formularios.json` |
| reCAPTCHA habilitado | 40 sí (interruptor por formulario) · clave de prueba: pendiente de ver en pantalla | `11_formularios.json` |
| Banner y modal usan el mismo formulario | 40 sí | `10_paginas.json` |
| Portal declarado en la incrustación | 6925781 en las 80 | `10_paginas.json` |

---

## 1. Prueba de envío real sobre las 80 instancias

**No ejecutada.** Está lista para correr pero se detuvo a propósito en la ronda 3 porque:

1. Crea 80 contactos reales en el portal productivo y, si los Activadores funcionan, los asigna a
   ejecutivos de UDEP. Requiere decisión explícita y aviso previo al equipo comercial
   (`input/requirements.md` §4.0 y §7 pregunta 1).
2. El entorno donde corrió esta sesión no puede abrir udeponline.pe con el navegador automatizado
   (ver "Lo que no se pudo verificar"). En una máquina local no hay ese impedimento.

Lo que sí quedó verificado del lado web: las 40 páginas responden 200 (`00_preflight.json`, P6),
cada una incrusta el mismo formulario en banner y modal, y ninguna incrustación manipula campos
por JavaScript, salvo el bloque roto de *Liderazgo y Negociación de Conflictos* (`10_paginas.json`,
`instancias[].tiene_callbacks`).

## 2. Qué formulario se dispara en cada página

Sin envío no hay registro de disparo. Lo verificado por lectura del marcado: **el identificador
incrustado coincide con el esperado en las 40 páginas**, sin divergencias respecto de la medición
del 15 de septiembre (`10_paginas.json`, `divergencias: []`). El identificador que efectivamente
se registre en HubSpot queda para la ronda 3.

## 2 bis. Cruce con el canon Piura (pedido por Santiago el 16-sep)

Se cruzaron las 80 instancias (hero y modal de cada página) contra la planilla *Formularios de
Google (Piura)*, columna ID, resolviendo cada identificador por la API de HubSpot para saber a qué
formulario apunta de verdad. Regla aplicada: **la herramienta gana sobre la hoja**. Evidencia:
`21_cruce_canon.json`, `cruce_canon_vicente.csv` (80 filas), `cruce_canon_discrepancias.csv`.

| Resultado sobre 80 instancias | Cantidad |
|---|---|
| El formulario de la página coincide con el canon | **70** |
| Falsa alarma del canon: la página está bien, la planilla está mal | **6** (3 páginas) |
| La planilla no tiene fila para la página | **4** (2 páginas) |
| **Discrepancia real** (la página apunta a un formulario de otro programa) | **0** |

**Conclusión para Vicente: no hay que cambiar el identificador en ninguna de las 40 páginas.** Las
diferencias con la planilla son errores de la planilla:

- *Liderazgo y Negociación de Conflictos* (fila 3) y *Gestión del Talento y Negociación de
  Conflictos* (fila 7) comparten el ID `43632e61` y tienen los nombres cruzados, tal como advirtió
  Santiago. Por API, `43632e61` es "PIURA: PDE en Liderazgo y Negociación de Conflictos (UDN
  UDEP)". El sitio sirve `84f82226` ("Liderazgo y Negociación de Conflictos Piura") y `0c7b3436`
  ("PDE en Gestión del Talento y Negociación de Conflictos"), ambos correctos para su página.
- *Digital Business Model* (fila 30): el canon dice `b92183d3` ("Curso Digital Business Model
  (UDN UDEP)") y el sitio usa `00b12055` ("Curso Digital Business Model Piura (UDN UDEP)"). Son
  dos formularios distintos para el mismo curso, ambos activos y ambos inscriptos en el Activador
  de Cursos. El de la página corresponde al curso; el del canon no fue normalizado el 15-sep
  (`13_formularios_canon.json`).
- Sin fila en la planilla: *Analítica Digital & Growth Marketing* (`7a38b319`, creado el 15-sep) y
  *Diplomado en Inteligencia Emocional y Coaching* (`bef4306e`).
- Filas del canon que no corresponden a ninguna página: fila 34 "Marketing Digital Test" sin ID,
  fila 37 duplicada de Comunicación Efectiva y Gestión del Talento con un ID de Meta
  (`1901549703874911`), y filas 45 y 46 con anotaciones en vez de datos. La fila 19 tiene la URL
  mal escrita ("enfelicidad") y la fila 35 una URL que no existe; en ambas el ID sí coincide con
  el sitio.

**Hallazgo derivado:** existen formularios duplicados y activos para el mismo programa
(`43632e61` junto a `84f82226`; `b92183d3` junto a `00b12055`), y los dos duplicados están
inscriptos en Activadores. `43632e61` conserva el valor de programa correcto ("Liderazgo y
Negociación de Conflictos") mientras que `84f82226`, el que usa la página, envía "Marketing
Digital y Ecommerce" desde la normalización. Conviene decidir cuál es el canónico de cada par y
archivar el otro, para que no vuelvan a mezclarse en la planilla.

## 3. Activador de cada formulario

Los Activadores **no son uno por programa: son seis workflows por clúster**, todos activos, que se
disparan por envío de formulario y cuya única acción es inscribir al contacto en el workflow de
asignación (`output/evidencia/flows/*.json`, `enrollmentCriteria` y `actions`). Se revisaron los
1083 workflows del portal.

| Activador | Formularios de UDEP que inscribe |
|---|---|
| 0305. Activador Cursos Piura | 15 cursos |
| 0305. Activador Diplomados Piura | 5 diplomados |
| 0302. Activador Clúster Marketing Digital Piura | 1 diplomado + 2 programas |
| 0303. Activador Clúster Habilidades de Gestión Piura | 8 programas |
| 0301. Activador Clúster Liderazgo y Gestión de Personas | 5 programas |
| 0307. Activador Clúster Emprendimiento, Innovación y Tecnología | 3 programas |

**Hallazgos:**

- **Crítico · sin Activador:** *Curso Analítica Digital & Growth Marketing* (`7a38b319`). Ningún
  workflow lo referencia. Es el formulario que Vicente creó el 15 de septiembre para separar este
  curso del de Marketing Digital; el Activador de Cursos no lo incluye. Cada lead que entre por
  ahí no se asigna.
- **A revisar · clúster que no cuadra por nombre:** *Diplomado en Marketing Digital y Ecommerce*
  (`243be113`) entra por el clúster Marketing Digital y no por el de Diplomados; *PDE en Gestión
  del Cambio y Negociación de Conflictos* (`9359c5fb`) entra por Emprendimiento, Innovación y
  Tecnología cuando por tema correspondería a Habilidades de Gestión. Pueden ser decisiones
  comerciales; hay que confirmarlo con quien administra los Activadores.
- Los 37 restantes están referenciados por exactamente un Activador, en sus criterios de
  inscripción (`12_activadores.json`, `en_criterios_de_inscripcion: true`).
- Que el Activador **se ejecute** para un lead concreto (H5) solo se prueba enviando. Pendiente.

## 4. Inventario de campos y estandarización

Los 40 se leyeron por API sin un solo error 403: **el token de 5minutos sí puede leer los cuatro
que a Vicente le devuelven 403** (`11_formularios.json`, `errores: []`). Los 40 tienen ocho
campos.

**36 formularios son idénticos a la plantilla** en nombres, etiquetas, obligatoriedad y orden, con
una variante esperable: los 24 de programas y diplomados usan la propiedad de *programas* en lugar
de la de *cursos* para el campo oculto. Los 36 tienen la cláusula de autorización de datos, el
encabezado "¿QUIERES MÁS INFORMACIÓN?" y el mensaje de confirmación correcto. Fueron actualizados
por API el 15 de septiembre entre las 13:24 y las 13:31, lo que coincide con la normalización que
hizo Vicente (`11_formularios.json`, `actualizado`).

**Los 4 que Vicente no pudo escribir** tienen su última modificación el 11 de junio y acumulan
todos los desvíos:

| Formulario | Desvíos respecto de la plantilla |
|---|---|
| *Curso Coaching* (`294bab20`) | etiqueta "Apellidos"; correo antes que teléfono; medio de contacto no obligatorio; el mensaje va a la propiedad genérica de HubSpot, no a la de UDEP; sin cláusula de datos; sin encabezado; sin mensaje de confirmación; sin valor de programa |
| *Curso Inteligencia Emocional* (`c1438a54`) | etiquetas "Apellidos" y "Correo"; el mensaje va a la propiedad genérica; sin cláusula; sin encabezado; sin confirmación; sin valor de programa |
| *Curso Marketing Digital* (`b6e43bcf`) | etiquetas "Apellidos" y "Correo"; teléfono no obligatorio; **la propiedad de programa no lleva el sufijo de UDEP** (es otra propiedad); el mensaje va a la propiedad genérica; sin cláusula; sin encabezado; sin confirmación; sin valor de programa |
| *Curso Negocios E-commerce* (`66f1f7d0`) | etiquetas "Apellidos" y "Correo"; teléfono no obligatorio; sin cláusula; sin encabezado; sin confirmación; sin valor de programa |

Precisión sobre lo que decía el correo de Vicente: en estos cuatro, la propiedad de *medio de
contacto* **sí** lleva el sufijo. Lo que está mal es el *mensaje* (tres de los cuatro escriben en la
propiedad genérica de HubSpot) y, en *Marketing Digital*, la propiedad de programa.

**El hallazgo grande: el campo oculto de programa.** Cada formulario lleva un campo oculto cuyo
valor por defecto es el nombre del programa, y eso es lo que HubSpot guarda en el contacto como
programa de interés. Lo que se observa (`11_formularios.json`, `valor_programa`):

- Los 14 cursos normalizados envían **"Gestión del Talento"**, sea cual sea el curso. Solo es
  correcto en *Curso Gestión del Talento*.
- Los 24 programas y diplomados envían **"Marketing Digital y Ecommerce"**. Solo es correcto en
  *PDE en Marketing Digital y E-commerce*.
- Los 4 de junio no envían ningún valor.
- *Analítica Digital & Growth Marketing* no puede enviar el valor correcto aunque se edite: la
  propiedad de cursos **no tiene una opción para ese curso** (`11_formularios.json`, `opciones`).

**Hipótesis, no hecho.** Que el valor sea exactamente el de la plantilla en los 14 cursos, la
primera opción de la lista en los 24 programas, y que los 36 se hayan actualizado en la misma
ventana de siete minutos, es compatible con que la normalización del 15 de septiembre haya
escrito el valor oculto de la plantilla sobre todos. No se puede probar el valor anterior por API
(no hay historial de versiones de formulario). Se confirma o descarta preguntándole a Vicente qué
valor envió su script. Lo que sí es hecho, y lo que hay que corregir, es el valor actual.

Consecuencia: los Activadores enrutan bien porque se disparan por formulario, no por este campo.
Pero el ejecutivo recibe un lead cuyo programa de interés dice "Gestión del Talento" cuando la
persona pidió información de Transformación Digital, y los reportes por programa quedan mal desde
el 15 de septiembre.

## 5. Unidad de negocio y tipo de suscripción

**No verificable por la API de formularios**: la respuesta no incluye unidad de negocio ni tipo de
suscripción para ninguno de los 40 (`11_formularios.json`, `unidad_de_negocio:
NO_EXPUESTO_POR_API`). La cláusula legal de los 36 normalizados referencia el tipo de suscripción
608587966; los 4 de junio no tienen cláusula, por lo tanto tampoco tipo de suscripción asociado.
La confirmación de marca hay que hacerla en la interfaz de HubSpot, formulario por formulario, o
por la vista de unidades de negocio del portal.

---

## Los dos cursos nuevos (CA-2)

Se revisaron primero y su resultado va antes que el resto:

- ***Negocios Innovadores*** (`a44b1d7f`): definición igual a la plantilla, cláusula, encabezado y
  confirmación correctos, **un Activador** (Cursos). **Falla H3:** envía "Gestión del Talento".
  Un lead entra, se asigna, pero queda marcado como interesado en otro curso.
- ***Analítica Digital & Growth Marketing*** (`7a38b319`): definición igual a la plantilla,
  cláusula, encabezado y confirmación correctos. **Falla H4:** ningún Activador lo referencia.
  **Falla H3 sin arreglo posible desde el formulario:** no existe la opción del curso en la
  propiedad. Hoy un lead de este curso entra al CRM, no se asigna a nadie y dice "Gestión del
  Talento".

## reCAPTCHA (CA-5)

- El interruptor de reCAPTCHA está **activado en los 40 formularios** (`11_formularios.json`,
  `recaptcha_habilitado: true`). Es una configuración por formulario.
- El HTML de las 40 páginas de WordPress **no contiene ninguna referencia a reCAPTCHA** ni a un
  complemento que lo cargue (`10_paginas.json`, `html_menciona_recaptcha: false`). Lo que se ve en
  pantalla viene de HubSpot.
- **Si es de portal o por formulario:** el interruptor es por formulario; la clave, en HubSpot, no
  es configurable por formulario, así que un aviso de "clave de prueba" no sería de un formulario
  en particular. **Esto es una inferencia sobre cómo funciona HubSpot, no evidencia de esta
  corrida.** La evidencia (el aviso "This reCAPTCHA is for testing purposes only" en pantalla) solo
  se obtiene abriendo el formulario con el navegador, que quedó para la ronda 3.
- **Alcance a UANDES:** si el aviso se confirma, alcanza a todos los formularios del portal
  6925781, incluidos los de UANDES Online. Hay que avisar a Rocío antes de tocar nada.

---

## Reparto A/B/C/D y qué implica para Vicente

| Caso | Cantidad | Qué es | Quién |
|---|---|---|---|
| **A** · nada que hacer | **2** | `d6c333ed` Gestión del Talento · `cd64140f` PDE Marketing Digital y E-commerce | — |
| **B** · editar el formulario, el identificador no cambia | **38** | 34 solo por el valor oculto de programa (y en dos, revisar el clúster) · 4 con normalización completa | 5minutos |
| **C** · repuntar la página | **0** | ninguna página apunta a un formulario de otro programa | — |
| **D** · crear formulario y repuntar | **0** | — | — |

**Vicente no tiene que repuntar ninguna página.** Los 40 identificadores son correctos y no
cambian. Lo que le toca a él es marcado de WordPress, no formularios:

1. **Limpiar la página de *Liderazgo y Negociación de Conflictos***: tiene ocho llamadas de
   incrustación en vez de dos; seis son copias de un bloque con los marcadores `HS_PORTAL_ID` /
   `HS_FORM_ID` sin resolver, apuntando al mismo contenedor del modal (`10_paginas.json`,
   `instancias`). El banner y la octava llamada sí tienen el identificador correcto. Si esos seis
   bloques producen renderizado duplicado o errores en consola se ve en la ronda 3.
2. **Título duplicado:** ver la sección "Título duplicado: 7 de agosto vs 36 de hoy" más abajo.
   En resumen: 36 páginas tienen hoy el título en WordPress y también dentro del formulario de
   HubSpot, sin CSS que oculte uno de los dos (`41_titulo_embeds.json`). Cuántas lo muestran dos
   veces en pantalla se confirma en la ronda 3. Cuando se corrijan los 4 restantes con la
   plantilla, quedarán en la misma situación (CA-6).
3. **Página `programas-de-especializacion-dev/`:** sigue publicada y responde 200, sin formularios
   (`10_paginas.json`, `paginas_extra`).

**Lo que le toca a 5minutos (caso B):**

- Corregir el valor oculto de programa en 34 formularios (uno por uno, o por API con el valor
  correcto de cada página; la tabla está en `tools/clasificar.py`, `PROGRAMA_ESPERADO`).
- Normalizar los 4 de junio con la plantilla completa: campos, sufijos, cláusula, encabezado,
  mensaje de confirmación y valor de programa. Avisar a Vicente en el mismo acto por el título
  (CA-6).
- Agregar el formulario de *Analítica Digital* al Activador de Cursos (o al que corresponda) y
  crear la opción del curso en la propiedad de cursos. **Ambas cosas modifican HubSpot y requieren
  su propia aprobación: esta corrida no las hizo.**
- Confirmar con quien administra los Activadores los dos clústeres a revisar.

---

## Verificaciones adicionales del 16 de septiembre

### Seguridad (P0): script de verificación falsa tipo ClickFix

Se buscó en el HTML servido de las 40 páginas y en los 38 archivos JavaScript propios del sitio
(tema y complementos de WordPress) el dominio `id-verif-code.info`, textos de "verificación
humana" fuera del reCAPTCHA legítimo, escritura al portapapeles, comandos de Windows
(PowerShell, mshta, cmd) y patrones de código ofuscado. **Resultado: cero indicadores en las 40
páginas y en los 38 scripts.** Todos los dominios desde los que se cargan scripts e iframes son
reconocidos (HubSpot, Google, Meta, Cloudflare, el propio sitio) (`40_seguridad.json`,
`evidencia/scripts/`).

**Límite de esta verificación:** se analizó lo que el servidor entrega a una petición normal. Una
inyección que se active solo en el navegador, o solo para ciertos visitantes (por país, por
dispositivo o desde Cloudflare), no se ve así. La confirmación final es abrir las páginas con el
navegador en la ronda 3 y revisar la consola y las peticiones de red.

### Título duplicado: 7 de agosto vs 36 de hoy

Son dos medidas distintas y no se contradicen:

- **Agosto (QA visual del 6 de agosto, planilla canon):** 7 páginas mostraban el título tres veces
  dentro del modal abierto, en pantalla. Cuatro de esas siete son los formularios de junio, que
  **no tienen encabezado en HubSpot**, así que la triplicación venía del marcado de WordPress al
  abrir el modal, no del formulario.
- **Hoy (HTML servido + API):** el título de WordPress está en el HTML de las 40 páginas (una vez
  en 20, dos veces en 14, tres veces en 5 y siete veces en *Liderazgo y Negociación*). Desde el
  15 de septiembre, 36 formularios traen además su propio encabezado dentro de HubSpot. Solo una
  página (*Liderazgo y Negociación*, en sus bloques rotos) tiene CSS que oculte el encabezado del
  formulario. Por eso **36 páginas tienen riesgo estructural de mostrar el título dos veces**, y
  el riesgo es nuevo: lo introdujo la normalización, no existía en agosto.
- **Lo que falta:** contar en pantalla, hero y modal por separado, en la ronda 3. Ese es el número
  que se le lleva a Vicente. Hasta entonces, el "36" es riesgo, no conteo (`41_titulo_embeds.json`).

Sobre "el embed nuevo": de las 40 páginas, 39 usan la incrustación plana (portal, formulario,
región y destino) y solo *Liderazgo y Negociación* usa el bloque nuevo con CSS y `onFormReady`,
en sus seis copias rotas. No se detectó un grupo de "3 cursos con embed nuevo" en el HTML actual;
si en agosto lo hubo, hoy no está o se homogeneizó (`41_titulo_embeds.json`, `firma_incrustaciones`).

### Reconciliación con los ítems de agosto

| Ítem de agosto | Estado hoy | Evidencia |
|---|---|---|
| `negocios-innovadores/` daba 404 | **Cerrado:** redirige (301) a `curso-de-negocios-innovadores/`, que responde 200 con formulario | `42_reconciliacion_agosto.json` |
| `programa-de-especializacion-enfelicidad-…` daba 404 | Sigue 404, pero es un error de la planilla (falta un guion); la página real responde 200. Corregido en la planilla propuesta | ídem |
| `curso-de-marketing-digital-test/` | 404: la página de prueba ya no existe. Quitar la fila 34 de la planilla | ídem |
| Diplomados en borrador (instructivo F) | **Cerrado:** las 6 páginas de diplomados responden 200 e incrustan su formulario | ídem, `10_paginas.json` |
| Fuga del modal (el modal no envía) | **Abierto:** solo se verifica enviando. Ronda 3 | — |
| Título en el modal | **Abierto:** ver sección anterior. Ronda 3 | — |
| `programas-de-especializacion-dev/` | Sigue publicada (200), sin formularios | ídem |

### Planilla canon Piura: propuesta corregida

`canon_piura_propuesta_corregida.xlsx` es una copia de la planilla con 17 cambios marcados en
amarillo y una hoja "Cambios 16-sep" que explica cada uno con su evidencia: los nombres y los ID
de las filas 3 y 7, el ID de Digital Business Model (fila 30), dos ID con barra al final, la URL
mal escrita de la fila 19, la URL de Negocios Innovadores, la fila 37 duplicada con un ID de Meta,
las URL que faltaban en las cuatro filas de diplomados, y dos filas nuevas (Analítica Digital y
el Diplomado en Inteligencia Emocional y Coaching). **No pisa la original**: es una propuesta para
que quien mantenga la planilla la revise y la aplique.

---

## Lo que no se pudo verificar, con el motivo

| Qué | Motivo | Cómo se cierra |
|---|---|---|
| R1 a R5 (render, campos en pantalla, envío aceptado, confirmación visible, cláusula legible) en las 80 instancias | La ronda 3 no corrió: variable `DRY_RUN` en 1 por decisión pendiente, y el navegador automatizado no pudo abrir el sitio desde este entorno (certificado del proxy de salida, error `ERR_CERT_AUTHORITY_INVALID`, `00_preflight.json` P5) | Correr la ronda 3 desde una máquina local con `DRY_RUN=0`, después de avisar al equipo comercial |
| H1, H2, H5 (contacto creado, atribución al formulario, Activador ejecutado) | Dependen del envío real | Ronda 3 |
| H6 (unidad de negocio y tipo de suscripción) | La API de formularios no lo expone | Revisión en la interfaz de HubSpot |
| Si el reCAPTCHA muestra la clave de prueba | Solo se ve en el formulario renderizado | Ronda 3 (captura del banner) |
| Si los seis bloques rotos de *Liderazgo y Negociación* duplican el formulario en pantalla (CA-7) | Solo se ve en el navegador | Ronda 3 |
| El valor oculto de programa **antes** del 15 de septiembre | La API no tiene historial de formularios | Preguntar a Vicente qué envió su script |

---

## Lo que encontramos y no pidió

- **El valor oculto de programa en 37 formularios** (sección 4). Es el hallazgo principal de la
  auditoría y no estaba en el correo.
- **La propiedad de cursos tiene opciones duplicadas y mal escritas**: "Negocios e-commerce",
  "Negocios Ecommerce" y "Negocios E Commerce" son tres opciones distintas; "Comunicación
  Efectiva" y "Comunicacio Efectiva" también. En la de programas hay dos opciones con formato
  interno ("liderazgo_y_felicidad_organizacional", "liderazgo_y_transformacion_digital")
  (`11_formularios.json`, `opciones`). Los reportes por programa cuentan por separado lo que es
  lo mismo.
- **No existe opción de programa para *Analítica Digital & Growth Marketing*.**
- **Los datos históricos en propiedades equivocadas:** tres de los cuatro formularios de junio
  escriben el mensaje en la propiedad genérica de HubSpot y *Marketing Digital* escribe el
  programa en una propiedad sin sufijo. Corregir el formulario detiene el problema; lo ya escrito
  no se mueve solo (§6 del requerimiento).
- **Los leads de *Analítica Digital* atribuidos a *Marketing Digital*** hasta el 14 de septiembre
  siguen así. Fuera de alcance, pendiente de decisión (§6).
- **Los 36 formularios normalizados llevan encabezado propio** y las páginas también: riesgo de
  título duplicado en 36 páginas, no solo en las 7 que reportó el QA de agosto. Pendiente de
  confirmar en pantalla.

---

## Decisiones que quedan para Moisés y Santiago

1. **Correr o no la pasada real de 80 envíos**, y cuándo. Recomendación: sí, desde una máquina
   local, con los Activadores encendidos, avisando antes al equipo comercial de UDEP. Sin eso no
   se cierran R1-R5, H1, H2, H5, el reCAPTCHA ni CA-7.
2. **Qué se le dice a Vicente ahora**: que no tiene que repuntar nada, que el problema del valor
   oculto probablemente viene de su normalización, y pedirle el valor que envió su script.
3. **Aprobar la edición de los 38 formularios caso B** y en qué orden. Propuesta: primero los dos
   cursos nuevos y el Activador de *Analítica Digital*, después los 4 de junio, después los 32
   restantes por API.
4. **Si el reCAPTCHA se confirma como clave de prueba, avisar a Rocío** antes de tocarlo.
5. **Migración de datos históricos y re-atribución** (§6): cotizar aparte o descartar.
6. **Fecha para Vicente**: ahora sí se puede fijar, porque el reparto ya está (38 B, 0 C, 0 D).

---

## Anexo técnico

**Archivos de evidencia** (todos en `output/`):

- `00_preflight.json` · seis comprobaciones de acceso.
- `10_paginas.json` + `evidencia/paginas/<slug>.html` · HTML crudo de las 40 páginas y cuerpo de
  cada llamada `hbspt.forms.create`.
- `11_formularios.json` + `evidencia/formularios/<formId>.json` · respuesta cruda de
  `GET /marketing/v3/forms/{formId}` para los 40.
- `12_activadores.json` + `evidencia/flows/<flowId>.json` · respuesta cruda de
  `GET /automation/v4/flows/{flowId}` de los seis Activadores; 1083 flows recorridos.
- `20_matriz.json` · 40 filas con hallazgos, severidad, caso y acción.
- `21_cruce_canon.json` + `13_formularios_canon.json` + `input/canon_piura.xlsx` · cruce de las 80 instancias
  contra la planilla Piura, con los dos formIds del canon resueltos por API.
- `cruce_canon_vicente.csv` (80 filas) y `cruce_canon_discrepancias.csv` (vacío: 0 discrepancias reales).
- `40_seguridad.json` + `evidencia/scripts/` · escaneo de ClickFix en 40 páginas y 38 scripts propios.
- `41_titulo_embeds.json` · título de WordPress, encabezado de HubSpot, CSS y firma de incrustación por página.
- `42_reconciliacion_agosto.json` · estado HTTP actual de las URL marcadas en agosto.
- `canon_piura_propuesta_corregida.xlsx` · planilla canon con 17 correcciones propuestas.
- `registro_pruebas.csv` · 80 filas (banner y modal por página) con R1-R5, H1-H7, caso y
  severidad; R1-R5, H1, H2 y H5 en PENDIENTE hasta la ronda 3.

**Propiedades internas mencionadas en el texto:**

| En el texto | Propiedad |
|---|---|
| campo oculto de programa (cursos) | `cursos_piura__udn_udep_` |
| campo oculto de programa (programas y diplomados) | `programas_piura__udn_udep_` |
| propiedad de programa sin sufijo (Marketing Digital) | `cursos_piura` |
| mensaje de UDEP | `mensaje` (sin sufijo también en la plantilla) |
| propiedad genérica de mensaje de HubSpot | `message` |
| medio de contacto | `medio_de_contacto__udn_udep_` |
| nivel de estudios | `nivel_de_estudios__udn_udep_` |

**Activadores (identificadores de workflow):** Cursos `1631969831` · Diplomados `1854523916` ·
Clúster Marketing Digital `1631988744` · Clúster Habilidades de Gestión `1631988748` · Clúster
Liderazgo y Gestión de Personas `1631981721` · Clúster Emprendimiento, Innovación y Tecnología
`1645743473`. Todos inscriben por `FORM_SUBMISSION / FILLED_OUT` y su única acción (`0-15`) es
inscribir en el workflow `1631981736`.

**Formularios por caso** (identificador corto → página):

- **A:** `d6c333ed` curso-de-gestion-del-talento · `cd64140f` programa-de-especializacion-en-marketing-digital-y-e-commerce.
- **B, normalización completa (junio):** `294bab20` coaching · `c1438a54` inteligencia-emocional · `b6e43bcf` marketing-digital · `66f1f7d0` negocios-e-commerce.
- **B, sin Activador y sin opción de programa:** `7a38b319` analitica-digital-growth-marketing.
- **B, solo valor oculto de programa (33):** el resto; lista completa con el valor esperado en `20_matriz.json` (`programa_esperado`).

**Condiciones de esta corrida:** sesión remota de Claude Code; agentes del paquete ejecutados como
scripts por el orquestador; ronda 1 corrida con P5 en FALLA por certificado del entorno (no por
accesos); ningún formulario, workflow ni página fue modificado; no se creó ningún contacto.
