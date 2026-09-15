# requirements.md — Verificación y normalización de formularios · UDEP Online
**Versión 2 · 15-sep-2026**

**Portal HubSpot:** 6925781 (compartido con UANDES Online)
**Sitio:** udeponline.pe (WordPress + Elementor, gestionado por Vicente Ham)
**Origen:** correo de Vicente Ham del 15-sep-2026, con copia a Rocío Narea, Jimena Jiménez, Pedro Vega y Sebastián Gómez
**Ejecuta:** Moisés Camargo · **Aprueba:** Santiago Roman
**Nivel de riesgo:** **Alto** — se escribe en un portal productivo y se dispara maquinaria comercial en vivo

---

## 1. La necesidad

Verificar por envío real, y dejar registrado, que los 40 formularios de producto de UDEP Online
capturan, atribuyen y enrutan correctamente; normalizar los cuatro que la API de Vicente no puede
escribir; y confirmar desde HubSpot la configuración que su token no tiene permiso para ver.

**El dolor real no es el diseño.** Hoy nadie puede afirmar que un lead de UDEP llega a quien tiene
que llegar. Tres evidencias, todas del propio correo:

- *Analítica Digital & Growth Marketing* no tenía formulario propio y enviaba sus consultas al del
  *Curso de Marketing Digital*. Sus leads entraron atribuidos a otro curso hasta el 14-sep.
- Los dos cursos nuevos no tienen un solo envío registrado y nunca se probaron.
- Cuatro formularios escriben en `medio_de_contacto` y `mensaje` sin el sufijo `__udn_udep_`, que
  son propiedades distintas. Ese dato no llega junto con el del resto.

---

## 2. Lo medido el 15-sep-2026

Se descargaron las 40 páginas de producto y se extrajo el inventario de incrustaciones.

| Hecho | Valor |
|---|---|
| Páginas de producto publicadas | **40** — 18 programas, 16 cursos, 6 diplomados |
| Formularios de HubSpot distintos | **40**, uno por página |
| Instancias renderizadas | **80** — banner + modal en cada página |
| ¿Banner y modal son el mismo formulario? | **Sí, en las 40** |
| Portal declarado en la incrustación | `6925781` en las 80 |
| reCAPTCHA en el marcado de WordPress | **ninguno**, ni plugin ni script |

**Consecuencia de alcance.** El envío llega al mismo sitio por los dos caminos. El trabajo se
divide en dos volúmenes:

- **80 casos de renderizado y confirmación en pantalla.** El modal se carga por JavaScript al
  abrirlo, independiente del banner. Puede fallar solo.
- **40 casos de verificación en HubSpot.** Contacto, atribución, programa, Activador y marca se
  comprueban una vez por formulario.

**Dos hallazgos no reportados por Vicente.** La página de *Liderazgo y Negociación de Conflictos*
tiene ocho incrustaciones —banner, modal y seis copias de un bloque con `HS_FORM_ID` sin
resolver—, siete de ellas apuntando al mismo contenedor `#hubspot-formulario`. Y existe una página
`programas-de-especializacion-dev/` publicada y en el sitemap.

---

## 3. Alcance

### Entra

1. **Prueba de envío real** sobre las 80 instancias, con registro por página y resultado.
2. **Identificación del formulario en cada envío:** dejar registrado el `formId` que efectivamente
   se disparó, no el que se supone que está en la página.
3. **Verificación del Activador:** para cada `formId`, confirmar que está referenciado por un
   workflow "Activador", que es exactamente uno, y que ese workflow corresponde al programa que la
   página referencia.
4. **Inventario de campos por API de formularios:** con el `formId`, obtener la definición real de
   cada uno de los 40 —nombres internos, etiquetas, obligatoriedad, orden, opciones de
   desplegable— y contrastarla contra la plantilla de referencia para determinar si existe
   estandarización o si hay campos erróneos o divergentes entre formularios.
5. Los dos cursos nuevos primero: *Negocios Innovadores* (`a44b1d7f`) y *Analítica Digital &
   Growth Marketing* (`7a38b319`).
6. **Normalización, a cargo de 5minutos**, de los cuatro que devuelven 403 a la API de Vicente:
   *Inteligencia Emocional* (`c1438a54`), *Negocios E-Commerce* (`66f1f7d0`),
   *Marketing Digital* (`b6e43bcf`), *Coaching* (`294bab20`), incluida la cláusula de autorización
   de datos y el mensaje de confirmación.
7. Confirmación de unidad de negocio y tipo de suscripción de los 40.
8. **Diagnóstico y corrección del reCAPTCHA** por parte de 5minutos, si la clave de prueba es de
   HubSpot.
9. Aviso a Vicente al corregir los cuatro, para que oculte el título de WordPress.

### No entra

- Rediseño de las páginas de producto.
- Migración de los leads históricos con el dato en la propiedad sin sufijo (ver §6).
- Re-atribución de los leads de *Analítica Digital* (§6).
- Modificar los flujos Activador: se verifican, no se tocan.

---

## 4. CA-1 · Prueba de envío — diseño de QA

### 4.0 El efecto secundario que hay que decidir primero

**No existe portal de pruebas.** Los 80 envíos se hacen contra el portal productivo 6925781. Cada
envío crea un contacto real, y si el Activador funciona —que es justamente lo que se quiere
comprobar— ese contacto **se asigna a un ejecutivo real y entra en la maquinaria de SLA**.

Consecuencias que no son teóricas: 80 contactos falsos en la base, hasta 40 asignaciones a
ejecutivos de UDEP, tickets de SLA abiertos, y ejecutivos trabajando leads inventados.

Pausar los Activadores durante la pasada eliminaría la contaminación, pero también haría imposible
verificar el punto 3 del alcance, que es el que más importa. **La recomendación es no pausarlos**,
y en su lugar: datos de prueba identificables, aviso al equipo de UDEP antes y después, y limpieza
verificada al cierre.

Esto necesita decisión explícita (§7, pregunta 2).

### 4.1 Convención de datos de prueba

Obligatoria, porque es lo que hace posible encontrar y borrar después.

| Campo | Valor |
|---|---|
| `firstname` | `QA` |
| `lastname` | `Prueba <slug-de-pagina>` |
| `email` | `qa+<slug>-<banner\|modal>-<AAAAMMDD>@5minutos.io` |
| `phone` | número de prueba único acordado, el mismo en los 80 |
| `mensaje` | `PRUEBA QA 5MINUTOS — <fecha> — NO GESTIONAR` |

El patrón de correo permite localizar los 80 con una sola búsqueda y garantiza que cada instancia
produce un contacto distinto, lo que a su vez permite distinguir si falló el banner o el modal.

### 4.2 Comprobaciones por instancia — las 80

| Id | Qué se revisa | Pasa si | No pasa si |
|---|---|---|---|
| R1 | El formulario se renderiza | Aparece en el contenedor esperado: inline en el banner, `#hubspot-formulario` en el modal | No aparece, o el modal queda vacío al abrir |
| R2 | Campos renderizados | Coinciden con la definición que devuelve la API para ese `formId` | Falta un campo, sobra uno, o difiere la obligatoriedad |
| R3 | El envío se acepta | El formulario confirma el envío sin error | Error en pantalla, o el botón no responde |
| R4 | Mensaje de confirmación | Aparece visible tras enviar; en el modal, sin necesidad de cerrarlo | No aparece, o queda tapado por el modal |
| R5 | Cláusula de autorización de datos | Presente y legible antes de enviar | Ausente |

### 4.3 Comprobaciones por formulario — las 40

| Id | Qué se revisa | Pasa si | No pasa si |
|---|---|---|---|
| H1 | Contacto | Existe el contacto con el correo de prueba | No se creó |
| H2 | Atribución | El envío queda registrado contra el `formId` de esa página | Queda contra otro formulario |
| H3 | Programa | El formulario corresponde al programa de la página, por nombre y por el valor de `cursos_piura__udn_udep_` | Apunta a otro programa |
| H4 | Activador | Existe exactamente un workflow "Activador" que referencia ese `formId` | Ninguno, más de uno, o uno de otro programa |
| H5 | Disparo | Ese workflow se ejecutó para el contacto de prueba | No se ejecutó |
| H6 | Marca | Unidad de negocio y tipo de suscripción = UDEP | Otra marca del portal |
| H7 | Definición de campos | Nombres internos, etiquetas, obligatoriedad y orden coinciden con la plantilla de referencia, y las propiedades llevan el sufijo `__udn_udep_` donde corresponde | Divergencia en cualquiera de los cuatro, o propiedad sin sufijo |

Formulario de referencia: *Curso Gestión del Talento Piura (UDN UDEP)* (`d6c333ed`).

### 4.4 Severidad — qué bloquea y qué no

| Severidad | Casos | Efecto |
|---|---|---|
| **Crítico** | H1, H2, H3, H4, H6, y H7 cuando la propiedad no lleva sufijo | Bloquea el cierre. Cero abiertos |
| **Alto** | R3, R4, R5, H5, y el modal que no carga | Bloquea salvo aceptación escrita de Santiago |
| **Medio** | H7 por etiqueta, obligatoriedad u orden; R2 | Se documenta y se agenda |
| **Bajo** | Tipografía, color, una o dos columnas, texto del botón | Se documenta, no bloquea |

La lógica del corte: un formulario feo que captura y enruta bien pierde leads por conversión; uno
bonito que atribuye al programa equivocado los pierde del todo.

### 4.5 Criterios de entrada — antes del primer envío

- [ ] Inventario de los 40 formularios obtenido por API, con campos y definición
- [ ] Inventario de workflows Activador y su `formId` asociado
- [ ] Convención de datos de prueba acordada y número de teléfono definido
- [ ] Equipo comercial de UDEP avisado, con la ventana horaria de la pasada
- [ ] Decidido si los Activadores corren o se pausan (§7, pregunta 2)

### 4.6 Criterios de salida — para dar por cerrada la pasada

- [ ] 80 de 80 instancias ejecutadas y registradas
- [ ] 0 defectos críticos abiertos
- [ ] 0 defectos altos abiertos, o aceptados por escrito por Santiago
- [ ] Los 80 contactos de prueba eliminados, verificado por consulta
- [ ] Los tickets de SLA generados por la pasada cerrados o eliminados
- [ ] Equipo de UDEP avisado del cierre

### 4.7 Registro

Una fila por instancia: página · instancia (banner o modal) · `formId` esperado · `formId`
registrado · fecha y hora · correo de prueba usado · R1 a R5 · H1 a H7 · severidad si falla ·
observación.

---

## 5. Resto de criterios de aceptación

### CA-2 · Cursos nuevos (MUST)
**DADO** que los dos cursos nuevos no tienen ningún envío registrado, **CUANDO** se ejecuta la
pasada, **ENTONCES** DEBEN probarse primero y su resultado DEBE comunicarse antes que el resto.

### CA-3 · Qué se hace con cada formulario (MUST)

La acción **no se decide de antemano**: sale del resultado de H2, H3 y H7 de cada página. Hasta
que no corra el inventario no se sabe cuántos casos cae en cada rama, y por eso tampoco se puede
comprometer esfuerzo antes (§7, pregunta 4).

| Caso | Condición | Acción | Quién | ¿Cambia el `formId`? |
|---|---|---|---|---|
| **A** | El formulario corresponde al programa y su definición cumple la plantilla | Nada | — | No |
| **B** | El formulario corresponde al programa pero su definición está mal | **Editar** en el editor de HubSpot | 5minutos | No |
| **C** | La página apunta a un formulario de otro programa, **y el del programa sí existe** | **Repuntar la página** al formulario correcto. No se toca ningún formulario | Vicente | No |
| **D** | La página apunta a un formulario de otro programa, **y no existe uno para ese programa** | **Crear** el formulario desde la plantilla de referencia y entregar el identificador nuevo para que se repunte la página | 5minutos crea · Vicente repunta | Sí |

**Preferir siempre editar sobre recrear.** Un formulario nuevo rompe la continuidad de la
atribución histórica de ese programa y obliga a Vicente a intervenir la página. Se crea solo en el
caso D, cuando no hay alternativa.

**Los cuatro formularios que Vicente no puede escribir** —`c1438a54`, `66f1f7d0`, `b6e43bcf`,
`294bab20`— son caso B por definición: el identificador es el correcto, lo que está mal es la
configuración. Se editan.

**El caso D ya ocurrió una vez** y es el precedente que valida la regla: *Analítica Digital &
Growth Marketing* enviaba al formulario de *Marketing Digital* porque no tenía uno propio. Vicente
lo creó el 14-sep (`7a38b319`) y repuntó la página.

**En cualquier caso B o D, el formulario resultante DEBE** quedar con los ocho elementos de la
plantilla en su orden y disposición, las propiedades con sufijo `__udn_udep_`, la cláusula de
autorización de datos con el texto que usan los demás, y el mensaje "Gracias, te contactaremos a
la brevedad."

**Guardarraíl:** ningún `formId` cambia sin que el nuevo se comunique a Vicente en el mismo acto,
junto con el aviso del encabezado de CA-6.

### CA-4 · Marca (MUST)
**CUANDO** se revisa cada formulario, **DEBE** reportarse su unidad de negocio y tipo de
suscripción, y señalarse los que no corresponden a UDEP.

### CA-5 · reCAPTCHA (MUST)
**CUANDO** se diagnostica, **DEBE** determinarse si la clave de prueba está a nivel de portal o por
formulario. **SI** es de HubSpot, **ENTONCES** 5minutos la corrige. **SI** además es de portal,
**ENTONCES** el cambio alcanza a los formularios de UANDES Online y DEBE informarse a Rocío antes
de aplicarlo — no por aprobación, sino porque cambia el comportamiento de su portal.

### CA-6 · Coordinación del encabezado (MUST)
**CUANDO** se corrige uno de los cuatro con la plantilla —que incluye encabezado—, **DEBE** avisarse
a Vicente en el mismo acto para que oculte el de WordPress en esa página. Sin ese aviso el título
se duplica.

### CA-7 · Página con ocho incrustaciones (MUST)
**CUANDO** se revisa *Liderazgo y Negociación de Conflictos*, **DEBE** reportarse si los siete
cargadores sobre `#hubspot-formulario` producen renderizado duplicado. Es marcado de WordPress: el
hallazgo va a Vicente.

---

## 6. Hallazgos fuera de alcance que hay que decidir

**Los datos en la propiedad sin sufijo.** Corregir el formulario detiene la hemorragia pero no
mueve lo ya escrito. Hay que decidir si se migra.

**Los leads de Analítica Digital.** Entraron atribuidos a *Curso de Marketing Digital* hasta el
14-sep. La atribución histórica y el reporte por curso están mal.

---

## 7. Preguntas abiertas

| # | Pregunta | A quién | Bloquea | Recomendación |
|---|---|---|---|---|
| 1 | ¿Los Activadores corren durante la pasada o se pausan? | Santiago | CA-1 | **Que corran.** Pausarlos hace inverificable H5, que es el punto del ejercicio |
| 2 | ¿Entran la migración de datos y la re-atribución de §6? | Santiago / Rocío | alcance | Declararlo como hallazgo aparte y cotizarlo por separado |
| 3 | ¿Qué fecha de entrega comprometemos? | Santiago | planificación | El correo de Vicente no fija fecha; pide saber los bloqueos temprano. La fecha la ponemos nosotros. **No se puede fijar antes del inventario**, porque el reparto entre casos A/B/C/D define el esfuerzo |

**Resueltas:** ejecuta Moisés · aprueba Santiago · las plantillas las corrige 5minutos · si el
reCAPTCHA es de HubSpot, lo corrige 5minutos · la acción sobre cada formulario se decide por el
árbol de CA-3, no de antemano.

**Dependencia con Vicente que hay que declararle ahora:** los casos C y D exigen que él intervenga
la página. No es un aviso al cierre, es una coordinación que conviene anunciar en la respuesta a su
correo, junto con el aviso del encabezado de CA-6.

---

## 8. Lo que solo se resuelve ejecutando

El alcance del reCAPTCHA no se ve desde fuera: no hay nada en el marcado de WordPress, así que
viene de HubSpot y solo se determina desde la configuración del portal.

La definición de campos de los 40 formularios tampoco está en el HTML: la carga HubSpot en tiempo
de ejecución. Se obtiene por la API de formularios.

Si la API responde 403 también a nuestro token —como le pasa a Vicente con la escritura—, el
inventario del punto 4 del alcance hay que hacerlo desde la interfaz, y eso cambia el esfuerzo.
Se verifica antes de comprometer fecha.

---

## 9. Qué sigue

Aprobado este documento: `design.md` con el procedimiento de la pasada y la plantilla normalizada,
y recién después la descomposición en tareas de ClickUp para Moisés.
