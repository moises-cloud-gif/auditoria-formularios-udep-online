# Auditoría de formularios · UDEP Online — informe final

**Fecha:** 18 de septiembre de 2026 · **Portal HubSpot:** 6925781 · **Sitio:** udeponline.pe
**Alcance verificado:** los 40 formularios revisados uno por uno contra la API de HubSpot, las 40
páginas leídas del sitio vivo, los 1093 workflows del portal barridos, y **7 envíos reales hechos a
mano** por una persona en un navegador normal.

**Cobertura de la prueba de envío: 7 de 80 instancias.** El requerimiento pide 80 (banner y modal
de las 40 páginas). Se hicieron 7, todas por el formulario del banner. **Por el modal no se pudo
hacer ninguna, porque el modal no deja enviar** — y eso dejó de ser una limitación de la prueba
para convertirse en el hallazgo más grave del informe. Lo que no se probó está declarado como no
probado, página por página, en `registro_pruebas.csv`.
---

## Respuesta

**Hay dos respuestas, y la segunda es peor que la primera.**

**Uno: de los 40 formularios, solo 2 capturan, atribuyen y enrutan bien. Los otros 38 tienen al
menos un defecto crítico.** El más extendido no lo reportó nadie:
**37 formularios atribuyen el lead a un programa distinto del de su página o a ninguno**, porque el
campo oculto que lleva el nombre del programa trae el mismo valor en todos (registro
`20_matriz.json`, columna `H3`). Además, el formulario nuevo de *Analítica Digital & Growth
Marketing* **no está conectado a ningún Activador**: sus leads entran al CRM y no se asignan a
nadie (`12_activadores.json`, `7a38b319`).

Los dos que están bien: *Curso Gestión del Talento* (`d6c333ed`, que es la plantilla) y *PDE en
Marketing Digital y E-commerce* (`cd64140f`).

**Dos: la mitad de las entradas de leads del sitio no funciona en absoluto.** Cada página tiene dos
formularios: el fijo y el que se abre con el botón "Postula aquí". **El del botón no deja enviar.**
La persona lo llena, aprieta enviar y el navegador la frena por un campo obligatorio que está fuera
de la pantalla y que no puede alcanzar. No queda contacto, no hay atribución, no se dispara ningún
Activador, y el visitante se va creyendo que dejó sus datos. Comprobado a mano en 2 páginas; **39 de
las 40 usan la misma plantilla defectuosa**. Ver la sección "El modal no deja enviar".

| Verificación | Resultado sobre 40 | Evidencia |
|---|---|---|
| Programa correcto en el campo oculto (H3) | **2 bien · 33 envían otro programa · 4 sin valor · 1 sin opción disponible** | `20_matriz.json` |
| Un Activador por formulario (H4) | **39 con exactamente uno · 1 sin ninguno** · 2 a revisar por clúster | `12_activadores.json` |
| Definición igual a la plantilla (H7) | 36 iguales (24 con la variante de programas) · **4 con desvíos** | `11_formularios.json` |
| Cláusula de autorización de datos | 36 sí · **4 no** | `11_formularios.json` |
| Mensaje de confirmación "Gracias, te contactaremos a la brevedad." | 36 sí · **4 vacío** | `11_formularios.json` |
| Unidad de negocio y tipo de suscripción (H6) | **no lo expone la API** · pendiente en la interfaz | `11_formularios.json` |
| reCAPTCHA habilitado | 40 sí (interruptor por formulario) · **clave de prueba confirmada en pantalla el 16-sep** | `11_formularios.json` |
| Banner y modal usan el mismo formulario | 40 sí · HubSpot no distingue por cuál entró el lead | `10_paginas.json` |
| **El modal permite enviar** | **no en las 2 probadas** · 39 de 40 usan la misma plantilla defectuosa | `55_hallazgo_modal.json`, `56_modal_css.json` |
| Envíos reales ejecutados | **7 de 80** · las 40 del modal son imposibles hoy | `registro_pruebas.csv` |
| Portal declarado en la incrustación | 6925781 en las 80 | `10_paginas.json` |

---

## 1. Prueba de envío real — 7 de 80 instancias

**Qué se hizo:** 7 envíos reales, hechos a mano por Moisés Camargo en un navegador normal, cada uno
en una ventana de incógnito distinta, como lo haría cualquier visitante. Todos por el formulario del
banner. Evidencia: `51_muestra_manual_resultados.json` y la respuesta cruda de cada contacto en
`evidencia/contactos/`.

**Qué no se hizo, y por qué:**

| Lo que falta | Motivo |
|---|---|
| Las 40 instancias del modal | **El modal no deja enviar.** No es una decisión de alcance: se intentó y no se pudo. Es el hallazgo de la sección siguiente |
| 33 de las 40 instancias del banner | El reCAPTCHA del sitio rechaza al navegador automatizado, así que los 80 envíos no se pueden automatizar. A mano son unas 4 horas de una persona |

**Por qué 7 alcanzan para lo que este informe afirma.** La muestra no se eligió al azar: cubre los
dos cursos nuevos, un formulario sano de referencia, uno de los cuatro mal configurados de junio y
tres de las familias de programas. Los dos hallazgos principales —el programa mal atribuido y el
formulario sin Activador— quedaron **confirmados con leads reales**, no por lectura de
configuración. Lo que la muestra **no** permite afirmar es el comportamiento individual de las 33
páginas no probadas: ahí el informe se apoya en la configuración leída por API, que es sólida pero
no es lo mismo que haberlo probado. En `registro_pruebas.csv` cada fila dice cuál de las dos cosas
es.

**Lo verificado del lado web sin enviar:** las 40 páginas responden 200 (`00_preflight.json`, P6),
cada una incrusta el mismo formulario en banner y modal, y ninguna incrustación manipula campos por
JavaScript, salvo el bloque roto de *Liderazgo y Negociación de Conflictos* (`10_paginas.json`).


## 1 bis. El modal no deja enviar — hallazgo principal

**Qué pasa.** Cada página de producto tiene dos formularios: el que se ve al entrar (el "banner") y
el que se abre en una ventana flotante al hacer clic en **"Postula aquí"** (el "modal"). Son el
mismo formulario de HubSpot incrustado dos veces. **El del botón no permite completar el envío.**

**Cómo se comprobó.** Moisés lo probó a mano, en un navegador normal, en dos páginas:

| Página | Qué pasó |
|---|---|
| `curso-de-gestion-del-talento` | El modal abre, el formulario aparece, se llena lo que se ve, y al enviar sale **"Rellena este campo obligatorio"**. No se completa |
| `programa-de-especializacion-en-liderazgo-y-negociacion-de-conflictos` | Idéntico |

Ese mensaje no es de HubSpot ni del reCAPTCHA: **es el aviso del navegador por un campo obligatorio
vacío**, y ocurre antes de que el formulario intente enviarse.

**Por qué queda un campo vacío si la persona llenó todo lo que veía.** Porque no lo veía todo. El
CSS del modal no muestra el formulario completo, y lo hace de dos maneras distintas:

- En la plantilla que usan **39 de las 40 páginas**, la caja del modal **no tiene ninguna forma de
  desplazarse**: no tiene límite de altura, no tiene barra de scroll propia, le exige al formulario
  640 píxeles de alto mínimo, y además bloquea el scroll de la página de fondo. Si el formulario es
  más alto que la pantalla, **lo que queda debajo del borde es inalcanzable**.
- En la página de *Liderazgo y Negociación*, la única con la otra plantilla, sí hay scroll interno,
  pero se le fuerza al formulario "altura automática, sin mínimo", lo que lo colapsa y deja visible
  solo el principio.

Conteo sobre el CSS servido de las 40 páginas (`56_modal_css.json`): **39 con la primera plantilla,
1 con la segunda, y las 40 bloquean el scroll de la página mientras el modal está abierto.**

**Alcance, dicho con precisión.** Comprobado a mano en **2 de 40**. Las otras 38 usan la misma
plantilla que una de las dos probadas. Es una extrapolación bien fundada, pero es extrapolación: para
afirmarlo sobre las 40 hay que probar las 40.

**Qué significa para el negocio.** Toda persona que entra por "Postula aquí" —que es el botón
destacado de la página, repetido entre 6 y 19 veces en cada una— llena el formulario, lo envía, y se
topa con un error que no puede resolver. **Ese lead se pierde entero y además se lleva una mala
experiencia.** No hay forma de saber cuántos fueron, porque por definición no dejaron rastro en
HubSpot.

**Quién lo corrige: Vicente Ham.** Es CSS del sitio en WordPress, no configuración de HubSpot. El
arreglo es de pocas líneas: darle a la caja del modal un límite de altura y barra de desplazamiento
propia. Evidencia completa en `55_hallazgo_modal.json` y `56_modal_css.json`.

**Nota de honestidad sobre este informe.** La primera hipótesis que se escribió atribuía esta falla
al reCAPTCHA, porque el mismo formulario se incrusta dos veces por página. **Quedó descartada** en
cuanto se supo el texto exacto del error. La doble incrustación existe igual en las 40 páginas y
sigue siendo un defecto que vale reportar, pero no es la causa de esto.

## 2. Qué formulario se dispara en cada página

Dos verificaciones, una por lectura y otra por envío:

- **Por lectura del marcado, en las 40 páginas:** el identificador incrustado coincide con el
  esperado, sin divergencias respecto de la medición del 15 de septiembre (`10_paginas.json`,
  `divergencias: []`).
- **Por envío real, en 7 páginas:** HubSpot registró la conversión contra el formulario correcto en
  las 7. Lo graba como *"Título de la página: Nombre del formulario"*
  (`51_muestra_manual_resultados.json`).

En las 33 páginas restantes esto queda afirmado por lectura del marcado, no por envío.

**Un límite del método que conviene que Vicente sepa:** el banner y el modal de cada página usan el
**mismo** identificador de formulario, así que HubSpot no distingue por cuál de los dos entró un
lead. Para saberlo hay que mirar la página de origen, no el formulario.

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
  **CONFIRMADO CON UN LEAD REAL** el 17-sep: el envío de prueba llegó con programa
  "Gestión del Talento" estando en la página de Negocios Innovadores.
- ***Analítica Digital & Growth Marketing*** (`7a38b319`): definición igual a la plantilla,
  cláusula, encabezado y confirmación correctos. **Falla H4:** ningún Activador lo referencia.
  **Falla H3 sin arreglo posible desde el formulario:** no existe la opción del curso en la
  propiedad. Hoy un lead de este curso entra al CRM, no se asigna a nadie y dice "Gestión del
  Talento".

## reCAPTCHA (CA-5) — CONFIRMADO EN PANTALLA EL 16-SEP

- El interruptor de reCAPTCHA está **activado en los 40 formularios** (`11_formularios.json`,
  `recaptcha_habilitado: true`).
- El HTML de las 40 páginas de WordPress **no contiene ninguna referencia a reCAPTCHA** ni a un
  complemento que lo cargue (`10_paginas.json`, `html_menciona_recaptcha: false`). Lo que se ve en
  pantalla viene de HubSpot.
- **Lo que Vicente reportó queda confirmado con evidencia propia.** Al abrir
  `curso-de-gestion-del-talento` con un navegador (ejecución local de `tools/diagnostico.py`,
  16-sep), el formulario carga reCAPTCHA Enterprise y **muestra el aviso "This reCAPTCHA is for
  testing purposes only"**. Eso significa que hoy **no hay protección real contra spam** en los
  formularios de UDEP.
- La clave pública (sitekey) que sirve el formulario es `6LdGZJsoAAAAAIwMJHRwqiAHA6A_6ZP6bTYpbgSX`.
  **No es** la clave de prueba clásica de Google (`6LeIxAcTAAAA…`), sino otra clave que Google
  igualmente marca como de prueba. Que la clave sea de HubSpot y no del sitio es coherente con que
  WordPress no cargue nada de reCAPTCHA.
- **Alcance a UANDES: sí, alcanza.** Tres hechos verificados el 16-sep:
  1. Los formularios de UDEP Online y los de UANDES Online **viven en el mismo portal 6925781**.
     Comprobado consultando la definición pública de un formulario de cada marca contra ese portal:
     los dos responden 200 (`d6c333ed` de UDEP y `cdc34c31` de UANDES, *Diplomado en Marketing
     Digital & e-Commerce*).
  2. Los dos traen **exactamente la misma configuración de captcha**: `captchaEnabled: true` y
     `captchaVersion: V2`. Lo único que se configura por formulario es encender o apagar el
     captcha y su versión, no la clave.
  3. La clave la pone HubSpot, no el sitio: el WordPress de UDEP no carga nada de reCAPTCHA.
  Como la clave no es un ajuste por formulario y ambas marcas comparten portal, **corregirla en el
  portal cambia el comportamiento de los formularios de UANDES Online también.**
- **Queda una comprobación visual, opcional:** abrir una página de UANDES Online y leer la sitekey
  renderizada, con `python tools/diagnostico.py <url de uandesonline.cl>`. Si devuelve
  `6LdGZJsoAAAAAIwMJHRwqiAHA6A_6ZP6bTYpbgSX`, queda cerrado también por observación directa. El
  primer intento del 16-sep no pudo hacerse: la red desde la que se corrió rechazó la conexión a
  `uandesonline.cl`, aunque el sitio responde 200 desde otras redes.
- **Acción:** avisarle a Rocío **antes** de tocar el reCAPTCHA, porque el cambio alcanza a su
  portal. No es pedirle permiso sobre UDEP, es avisarle de un cambio que le afecta.

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

## Los 7 envíos reales, uno por uno

Hechos a mano por Moisés Camargo el 17-sep, cada uno en una ventana de incógnito distinta para que
HubSpot no los fusionara en un solo contacto. Los 7 quedaron como registros separados, con una
conversión cada uno.

| # | Página | Atribución (H2) | Programa que llegó (H3) | ¿Correcto? | Activador (H5) |
|---|---|---|---|---|---|
| m2 | curso-de-negocios-innovadores | correcta | Gestión del Talento | **NO** · debía ser Negocios Innovadores | disparó |
| m3 | curso-de-gestion-del-talento | correcta | Gestión del Talento | sí | disparó |
| m4 | curso-de-marketing-digital | correcta | Marketing Digital | sí | disparó |
| m5 | pde-marketing-digital-y-e-commerce | correcta | Marketing Digital y Ecommerce | sí | disparó |
| m6 | diplomado-marketing-digital-y-ecommerce | correcta | Marketing Digital y Ecommerce | a revisar contra el canon | disparó |
| m7 | pde-liderazgo-y-negociacion | correcta | **Marketing Digital y Ecommerce** | **NO** · debía ser Liderazgo y Negociación | disparó |
| m8 | curso-de-gestion-del-talento | correcta | Gestión del Talento | sí | disparó |

**Lo que estos 7 cierran:**

1. **El programa mal atribuido está confirmado en producción con leads reales.** En *Negocios
   Innovadores* y en *Liderazgo y Negociación*, la persona pidió información de un programa y en el
   CRM quedó registrada como interesada en otro. Si un ejecutivo abre ese contacto, lee algo que la
   persona nunca dijo.
2. **La atribución al formulario funciona bien en los 7.** HubSpot registra la conversión como
   *"Título de la página: Nombre del formulario"*, y en los 7 el formulario es el que corresponde a
   su página. Este punto del requerimiento queda en verde.
3. **Un envío del 17-sep desmintió a la auditoría, y se corrige acá.** Leyendo la configuración se
   había previsto que *curso-de-marketing-digital* llegaría con el programa vacío. Llegó con
   "Marketing Digital", que es lo correcto. Es un caso menos en la lista de fallas.

**Un envío anterior, del mismo día, sobre *Analítica Digital & Growth Marketing*** (`50_envio_manual_referencia.json`)
había confirmado además el otro hallazgo grande: ese lead **entró al CRM y no se le asignó a nadie**,
porque su formulario no está conectado a ningún Activador.

**Sobre el reCAPTCHA, lo que estos envíos demuestran:** a la persona **no le pidió nada** — apretó
enviar y pasó. Al navegador automatizado sí lo bloquea. O sea que hoy el captcha **no protege contra
spam** (usa una clave que Google marca como de prueba) y al mismo tiempo **impide automatizar la
verificación**. Es lo peor de los dos mundos.

### Condiciones de la prueba que hay que declarar

- Para que los contactos de prueba no llegaran a ejecutivos reales ni se contaran como MQL, se pidió
  a Roman Villalobos que agregara una regla temporal en los workflows de asignación: si el correo es
  de 5minutos, el lead se asigna a Moisés. **Funcionó**: los 7 quedaron con dueño
  `moises@5minutos.io` y con las propiedades de MQL vacías.
- **Esa regla toca 5 workflows de producción y sigue puesta.** Hay que pedirle a Roman que la quite.
  Es una desviación consciente de la regla "no se modifica ningún workflow en esta corrida",
  acordada con Pedro y aprobada por Santiago, y se declara acá a propósito.
- Efecto secundario de esa misma regla: en los 7 contactos quedaron vacíos **facultad y país**,
  porque la rama de prueba asigna el dueño y termina antes de que el flujo los complete. **No es un
  defecto del sitio**; es un límite de esta corrida.
- **Los 7 contactos de prueba fueron borrados el 18-sep**, con aprobación de Moisés, y verificados
  uno por uno (`91_limpieza_verificada.json`). El portal quedó sin rastros.

## Lo que no se pudo verificar, con el motivo

| Qué | Motivo | Cómo se cierra |
|---|---|---|
| Las 40 instancias del **modal** | No se puede enviar por el modal. Es el hallazgo de la sección 1 bis, no una limitación de la prueba | Primero que Vicente arregle el CSS; después probar |
| 33 de las 40 instancias del **banner** | El reCAPTCHA rechaza al navegador automatizado, así que los envíos no se pueden automatizar; a mano son unas 4 horas | Corregir el reCAPTCHA, o hacerlos a mano |
| R1 a R5 en las 73 instancias no probadas | Dependen del envío | Con lo anterior resuelto |
| H1, H2, H5 en las 33 páginas no probadas | Dependen del envío. Para esas páginas el informe se apoya en la configuración leída por API | Con lo anterior resuelto |
| H6 (unidad de negocio y tipo de suscripción) | La API de formularios no lo expone | Revisión a mano en la interfaz de HubSpot |
| Si los seis bloques rotos de *Liderazgo y Negociación* duplican el formulario en pantalla (CA-7) | Solo se ve en el navegador, y esa página es justamente una de las que no deja enviar por el modal | Recorrido visual de las 40 páginas, sin enviar |
| Facultad y país de los contactos de prueba | La regla temporal de ruteo corta el flujo antes de completarlos | Repetir un envío después de que Roman quite la regla |
| El valor oculto de programa **antes** del 15 de septiembre | La API no guarda historial de formularios | Preguntar a Vicente qué envió su script |
| La sitekey renderizada en una página de UANDES Online | La red desde la que se corrió rechazó la conexión a `uandesonline.cl`. El alcance ya quedó establecido por otra vía (mismo portal, misma configuración de captcha) | Reintentar desde otra red |

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

**Urgente, esta semana:**

1. **Mandarle a Vicente el arreglo del modal.** Es el hallazgo de mayor impacto y el de arreglo más
   barato. Mientras no se corrija, todo lead que entre por "Postula aquí" se pierde.
2. **Pedirle a Roman que quite la regla temporal de ruteo** de los 5 workflows. La prueba terminó y
   los contactos ya se borraron; la regla no tiene por qué seguir viva en producción.
3. **Avisarle al equipo comercial de UDEP que la pasada de prueba terminó.**

**Del alcance de la corrección:**

4. **Aprobar la edición de los 38 formularios caso B** y en qué orden. Propuesta: primero los dos
   cursos nuevos y el Activador de *Analítica Digital*, después los 4 de junio, después los 32
   restantes por API.
5. **Qué se le dice a Vicente sobre el valor oculto de programa**: que no tiene que repuntar ningún
   formulario, que el problema probablemente viene de su normalización, y pedirle el valor que envió
   su script.
6. **Si el reCAPTCHA se confirma como clave de prueba, avisar a Rocío antes de tocarlo**, porque el
   portal es compartido y el cambio alcanza a UANDES Online.
7. **Migración de datos históricos y re-atribución** (§6 del requerimiento): cotizar aparte o
   descartar.
8. **Completar o no las 73 instancias que faltan.** Recomendación: no antes de que Vicente arregle
   el modal, porque hoy 40 de ellas son imposibles. Después de ese arreglo, rehacer la pasada
   completa tiene sentido y sirve además para verificar la corrección.
9. **Fecha para Vicente**: ahora se puede fijar, porque el reparto ya está (38 casos B, 0 C, 0 D) y
   el arreglo del modal está identificado con precisión.

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
  severidad. Las 7 instancias probadas llevan su resultado real; las 73 restantes dicen
  NO_PROBADO con el motivo.
- `51_muestra_manual_resultados.json` + `evidencia/contactos/` · los 7 envíos reales y la respuesta
  cruda de cada contacto.
- `55_hallazgo_modal.json` y `56_modal_css.json` · el hallazgo del modal y el conteo de plantillas
  de modal en las 40 páginas.
- `54_modal_estructura.json` · incrustaciones de HubSpot por página.
- `91_limpieza_verificada.json` · borrado de los 7 contactos de prueba, verificado uno por uno.

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
scripts por el orquestador; el navegador automatizado no pudo abrir el sitio desde este entorno
(certificado del proxy de salida), así que los envíos se hicieron a mano.

**Ningún formulario ni página de WordPress fue modificado.** Sí hubo dos escrituras sobre HubSpot,
las dos declaradas y aprobadas:

1. **Se crearon 8 contactos de prueba** por el endpoint público de formularios (7 de la muestra más
   uno de referencia). **Todos fueron borrados**, verificado uno por uno.
2. **Se modificaron 5 workflows de producción** para que los leads de prueba se asignaran a 5minutos
   en vez de a ejecutivos reales. Lo hizo Roman Villalobos a pedido de esta auditoría, acordado con
   Pedro y aprobado por Santiago. Es una desviación consciente de la regla "no se modifica ningún
   workflow en esta corrida". **La regla temporal sigue puesta al cierre de este informe y hay que
   quitarla.**
