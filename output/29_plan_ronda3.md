# Plan de la Ronda 3 · pendiente de aprobación de Moisés

**Estado:** NO EJECUTADO. Preflight en PASA (P1–P6). `DRY_RUN=0` ya viene puesto en el entorno,
así que la primera corrida de `tools/probar_envios.py` enviaría de verdad. Nada se ejecuta hasta
que este plan esté aprobado.

## 1 · Alcance

| | |
|---|---|
| Páginas | 40 (las de `input/paginas.json`, reconfirmadas por P6: 40/40 en HTTP 200) |
| Instancias | 80 = 40 banner + 40 modal |
| Contactos nuevos en el portal productivo | hasta 80, todos con propietario Moisés |
| Ya existentes de la muestra manual | 7, que siguen vivos |
| Pasada del probador | 1 de 3 (tope de `LOOP.md`) |

## 2 · Correos: hay que acortar el patrón antes de correr

`hs.correo_qa()` arma hoy `qa+<slug>-<banner|modal>-<AAAAMMDD>@5minutos.io`. Con los slugs reales
eso da una parte local de hasta **115 caracteres**, y el máximo que admite el RFC 5321 son 64.
**48 de las 80 instancias se pasan del límite.** Si la validación del formulario las rechaza, la
auditoría registraría 48 formularios como rotos cuando el roto sería el correo de prueba.

Cambio propuesto, contenido en `tools/lib/hs.py` (`correo_qa` sólo se usa en `probar_envios.py`):

    qa+p07-banner-20260917@5minutos.io      (22 caracteres de parte local)

`p07` es el índice de la página en `input/paginas.json`, estable y reproducible. Se mantienen las
palabras `banner` y `modal` literales para que el patrón de `limpiar_pruebas.py` las siga
reconociendo. La correspondencia `p07 -> slug` queda escrita en `output/30_envios.json` y en el
registro CSV, así que cada contacto se sigue trazando a su página.

## 3 · El modal: qué se mide y cómo se registra

El hallazgo de `output/55_hallazgo_modal.json` dice que el modal se dibuja pero una persona no
puede enviarlo, porque hay campos obligatorios fuera de la caja visible y no hay forma de
desplazarse. Playwright sí los alcanza: `fill()` desplaza el elemento aunque el contenedor esté en
`overflow:hidden`. **Un modal que “pasa” automatizado seguiría estando roto para un humano.**

Por eso el modal se envía igual —es la única manera de saber si la atribución y el Activador
funcionan desde esa instancia— pero **la geometría se mide antes de tocar nada** y queda en la
evidencia. Campos nuevos por instancia en `30_envios.json`:

| Campo | Qué guarda |
|---|---|
| `campos_obligatorios` | nombres de los campos `required` del formulario |
| `campos_obligatorios_fuera_de_vista` | los que caen fuera del área visible, medidos **antes** de cualquier desplazamiento programático |
| `boton_enviar_fuera_de_vista` | si el botón de envío es inalcanzable |
| `modal_tiene_scroll_interno` | `scrollHeight > clientHeight` en la caja del modal |
| `pagina_scroll_bloqueado` | si `html.modal-open{overflow:hidden}` está activo |
| `alcanzable_por_humano` | falso si algún obligatorio o el botón quedan fuera de vista |
| `envio_requirio_alcance_no_humano` | verdadero si el script tuvo que tocar un campo inalcanzable |
| `veredicto_humano` | `ENVIABLE_POR_PERSONA` · `ROTO_PARA_PERSONA_ENVIABLE_SOLO_AUTOMATIZADO` · `ROTO_PARA_AMBOS` |
| `captura_vista_humana` | captura **del viewport**, lo que la persona ve |

Ese último punto corrige un defecto del script actual: hoy captura el *elemento* iframe, que sale
dibujado entero incluso en la parte recortada. Es justo la captura que haría parecer sano un modal
roto. Se conservan las dos (la del iframe y la del viewport) y la que manda para juzgar la
experiencia humana es la del viewport. La misma medición se hace en el banner, porque es barata y
da la línea de base.

**Lo que esto no hace:** no corrige el CSS. Regla 6 del proyecto.

## 4 · Orden de corrida

`LOOP.md` manda tandas de 10 con verificación en HubSpot entre tandas. Se agrega una tanda cero:

    python3 tools/probar_envios.py --desde 0 --hasta 1     # 1 página, 2 instancias
    python3 tools/verificar_contactos.py                   # ¿se creó el contacto?

Si esa página no crea contacto, se para. Recién después:

    --desde 1 --hasta 10   -> verificar_contactos.py
    --desde 10 --hasta 20  -> verificar_contactos.py
    --desde 20 --hasta 30  -> verificar_contactos.py
    --desde 30 --hasta 40  -> verificar_contactos.py

Cierre de la ronda: `tools/verificar_evidencia.py` (cuenta 80 instancias, captura en disco e
`hs_object_id` que responde en el portal) y `tools/registro.py`.

## 5 · Lo que NO se toca

- Ningún formulario, workflow ni página del sitio.
- Ningún contacto se borra. La limpieza sigue pendiente de aprobación.
- Sin MCP de HubSpot, sin llamadas a la API a mano, sin leer el archivo de secretos.

## 6 · Dos cosas que hay que decidir aparte

**a) La limpieza no alcanza a los 7 contactos de la muestra manual.**
`limpiar_pruebas.py` sólo borra correos que cumplen exactamente
`qa+<algo>-<banner|modal>-<AAAAMMDD>@5minutos.io`. Los de la muestra son `qa+manual-20260917@…`
y `qa+m2-…` a `qa+m8-…`: no cumplen el patrón, así que el script los lista como EXCLUIDOS y no los
toca. Si la intención es que entren en la limpieza final, hay que ampliar el patrón. Es un cambio
al script de borrado y no se hace sin decisión explícita.

**b) `instancia_planeada` en la muestra manual.**
m7 y m8 figuran como modal y sí crearon contacto, lo que choca con el hallazgo de que el modal no
envía. El campo se llama "planeada", no "confirmada". Además banner y modal incrustan el **mismo**
`formId` en la misma página, así que la atribución de HubSpot no puede distinguir una instancia de
la otra: lo único que las separa es la evidencia del navegador. Conviene que Moisés confirme cómo
completó esos dos envíos (si tuvo que bajar el zoom, por ejemplo) antes de que el informe afirme
nada sobre el modal.
