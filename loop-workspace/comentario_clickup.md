# Comentario para pegar en la tarea de ClickUp 86akjhh59

Adjuntar: `informe_formularios_udep.md` y `registro_pruebas.csv`.

---

**Auditoría de formularios UDEP Online — informe final (18-sep-2026)**

Repositorio con todo el trabajo y la evidencia:
https://github.com/moises-cloud-gif/auditoria-formularios-udep-online/tree/claude/informe-github-repo-2xu2ep

**Los dos hallazgos principales**

1. **El formulario del modal no deja enviar.** Cada página tiene dos formularios: el fijo y el que
   se abre con el botón "Postula aquí". El del botón se dibuja, la persona lo llena, y al enviar el
   navegador la frena por un campo obligatorio que está fuera de la pantalla y no se puede
   alcanzar. No queda contacto en HubSpot, no hay atribución y no se dispara ningún Activador.
   Comprobado a mano en 2 páginas; 39 de las 40 usan la misma plantilla de modal. **Lo corrige
   Vicente: es CSS del sitio, no HubSpot.**

2. **37 de 40 formularios atribuyen el lead a un programa que no es el de su página.** El campo
   oculto que lleva el nombre del programa trae el mismo valor en casi todos. Confirmado con leads
   reales en *Negocios Innovadores* y en *Liderazgo y Negociación de Conflictos*. Además,
   *Analítica Digital & Growth Marketing* no está conectado a ningún Activador: sus leads entran y
   no se asignan a nadie.

**Reparto de la corrección:** 2 formularios están bien (caso A), 38 hay que editarlos en HubSpot
(caso B). Ningún formId cambia, así que Vicente no tiene que repuntar ninguna página por este
motivo.

**Cobertura de la prueba, declarada sin maquillaje: 7 envíos reales de 80.** Los 40 del modal son
imposibles hoy porque el modal no envía. De los 40 del banner se hicieron 7, elegidos para cubrir
los dos cursos nuevos, un formulario sano de referencia, uno de los cuatro mal configurados de
junio y tres familias de programas. Las 33 páginas no probadas quedan afirmadas por lectura de la
configuración vía API, no por envío. En `registro_pruebas.csv` cada fila dice cuál de las dos cosas
es.

**Condiciones de la corrida que hay que declarar**

- Se crearon 8 contactos de prueba y **se borraron los 8**, verificado uno por uno.
- Se modificaron **5 workflows de producción** para que los leads de prueba se asignaran a 5minutos
  en vez de a ejecutivos reales. Lo hizo Roman Villalobos a pedido de la auditoría, acordado con
  Pedro y aprobado por Santiago. Es una desviación consciente de la regla "no se modifica ningún
  workflow", y **sigue puesta: hay que quitarla.**

**Lo que sigue**

1. Mandarle a Vicente el arreglo del modal (mayor impacto, menor costo).
2. Pedirle a Roman que quite la regla temporal de ruteo de los 5 workflows.
3. Avisarle al equipo comercial de UDEP que la pasada de prueba terminó.
4. Aprobar la edición de los 38 formularios caso B y su orden.
5. Si el reCAPTCHA se confirma como clave de prueba, avisar a Rocío antes de tocarlo: el portal es
   compartido con UANDES Online.
