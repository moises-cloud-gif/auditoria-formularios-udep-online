# Ronda 3 en tu computadora · paso a paso

Esta es la única parte de la auditoría que no se pudo hacer desde la sesión remota: abrir las 40
páginas con un navegador automático, llenar y enviar los 80 formularios (banner y modal), y
verificar en HubSpot que cada contacto se creó, quedó atribuido al formulario correcto y fue
asignado. Toma entre 40 y 60 minutos de máquina. Vos solo mirás y copiás comandos.

> **Antes de empezar, tres cosas que no son técnicas:**
> 1. Santiago tiene que haber aprobado la pasada real (crea 80 contactos reales en el HubSpot productivo).
> 2. El equipo comercial de UDEP tiene que estar avisado del día y la hora, para ignorar los leads
>    que empiezan con `qa+` y dicen "PRUEBA QA 5MINUTOS - NO GESTIONAR".
> 3. Los Activadores quedan encendidos. Es lo que se quiere probar.

---

## Paso 0 · Lo que necesitás tener instalado (una sola vez)

- **Python 3.10 o más nuevo.** En Windows: descargalo de python.org y, al instalar, marcá la casilla
  "Add Python to PATH". En Mac ya suele venir; si no, `brew install python`.
- **Git.** En Windows: git-scm.com. En Mac: viene con las herramientas de Xcode o `brew install git`.
- **Una terminal.** En Windows usá "PowerShell". En Mac, "Terminal".

Para comprobar que están, escribí en la terminal:

```bash
python --version
git --version
```

Si en Mac `python` no responde, usá `python3` en todos los comandos de esta guía.

## Paso 1 · Bajar el proyecto

```bash
cd Documentos
git clone https://github.com/moises-cloud-gif/auditoria-formularios-udep-online.git
cd auditoria-formularios-udep-online
git checkout claude/informe-github-repo-2xu2ep
```

Eso crea la carpeta `auditoria-formularios-udep-online` con todo el trabajo hecho hasta ahora.

## Paso 2 · Poner la llave de HubSpot

La llave **no está en GitHub** a propósito. Está en el paquete original de Roman (el zip del campo
"Link pre-entrega" de la tarea de ClickUp). Dentro de ese zip hay un archivo de configuración que
se llama `.env` (empieza con punto). Los scripts lo leen solos con la librería python-dotenv; vos
nunca tenés que copiar la llave a ningún otro lado.

1. Descomprimí el zip de Roman.
2. Copiá el archivo `.env` de esa carpeta a la carpeta `auditoria-formularios-udep-online`.
3. Abrilo con el Bloc de notas (o TextEdit). Vas a ver una línea que dice `DRY_RUN=1`. **Dejala así
   por ahora.** La vamos a cambiar en el paso 6.

Si no encontrás el archivo (en Windows y Mac los archivos que empiezan con punto están ocultos),
activá "ver archivos ocultos" en el explorador, o pedile a Roman que te lo mande de nuevo.

> **Trampa clásica de Windows:** si lo abrís con el Bloc de notas y guardás, Windows le agrega
> `.txt` al nombre y los scripts no lo encuentran. En el explorador activá "Extensiones de nombre
> de archivo" en la pestaña Vista, y confirmá que el nombre termine en `env` y nada más. Los
> scripts lo leen con la librería python-dotenv; vos no tenés que copiar la llave a ningún lado.

## Paso 3 · Instalar lo que usan los scripts (una sola vez)

```bash
pip install -r requirements.txt
python -m playwright install chromium
```

El segundo comando baja un navegador Chrome propio para la prueba. Tarda un par de minutos.

## Paso 4 · Comprobar que todo funciona

```bash
python tools/preflight.py
```

Tiene que terminar con `VEREDICTO: PASA` y las seis comprobaciones en `PASA`, incluida `P5`.
**Si dice FALLA, no sigas.** Para saber por qué, corré:

```bash
python tools/diagnostico.py
```

Ese comando no necesita la llave y te dice en castellano qué falta: si el archivo de configuración
está donde tiene que estar, si Windows le agregó `.txt`, si la llave se carga con python-dotenv, y
si el formulario se dibuja bien en la página. Pegame su respuesta si no queda claro.

Si querés ver el navegador mientras trabaja, útil cuando Cloudflare desconfía de un navegador
oculto, en Windows:

```bash
set PW_VISIBLE=1
python tools/preflight.py
```

En Mac, en vez de `set` usá `export PW_VISIBLE=1`. La misma variable sirve para el paso 7.

## Paso 5 · Ensayo en seco con dos páginas (no envía nada)

```bash
python tools/probar_envios.py --desde 0 --hasta 2
```

Con `DRY_RUN=1` el script abre las páginas, llena los campos, saca capturas y **no aprieta
enviar**. Sirve para ver que el navegador y los formularios se entienden. Al terminar, mirá la
carpeta `output/evidencia/`: tienen que haber aparecido cuatro imágenes nuevas (banner y modal de
dos páginas). Abrí una y fijate que se vea el formulario con los datos de prueba cargados.

Si las imágenes salen vacías o el script tira error, parate ahí y mandame el texto.

## Paso 6 · Activar la pasada real

Abrí el archivo `.env` con el Bloc de notas y cambiá:

```
DRY_RUN=1
```

por

```
DRY_RUN=0
```

Guardá. Desde este momento, cada corrida crea contactos de verdad.

## Paso 7 · Los 80 envíos, en cuatro tandas

Corré la primera tanda (10 páginas, 20 envíos):

```bash
python tools/probar_envios.py --desde 0 --hasta 10
```

Al terminar, verificá en HubSpot qué pasó con esos 20 contactos:

```bash
python tools/verificar_contactos.py
```

La última línea dice cuántos contactos se crearon, cuántos quedaron atribuidos al formulario
correcto y cuántos tienen ejecutivo asignado. **Si la primera tanda no creó ningún contacto,
parate ahí y avisame**: no tiene sentido seguir.

Si la primera tanda anduvo, seguí con las otras tres, corriendo la verificación después de cada una:

```bash
python tools/probar_envios.py --desde 10 --hasta 20
python tools/verificar_contactos.py

python tools/probar_envios.py --desde 20 --hasta 30
python tools/verificar_contactos.py

python tools/probar_envios.py --desde 30 --hasta 40
python tools/verificar_contactos.py
```

Cada tanda tarda entre 8 y 12 minutos. Podés dejar la computadora sola mientras corre.

## Paso 8 · Comprobar que la evidencia está completa

```bash
python tools/verificar_evidencia.py
python tools/registro.py
```

El primero cuenta: 80 instancias, cada una con captura y con identificador de contacto real. Tiene
que decir `VERIFICADOR PROGRAMATICO: PASA`. Si dice `FALLA`, abajo lista qué falta; mandame eso.
El segundo regenera `output/registro_pruebas.csv` con las 80 filas ya completas.

## Paso 9 · Mirar con tus propios ojos lo que el script no ve

Abrí en tu navegador normal dos o tres de las 40 páginas y fijate:

- Si al abrir el modal ("Postula") el título "¿QUIERES MÁS INFORMACIÓN?" aparece una o dos veces.
- Si debajo del formulario aparece el aviso "This reCAPTCHA is for testing purposes only".
- En *Liderazgo y Negociación de Conflictos*, si el modal muestra uno o varios formularios.

Anotá lo que veas. Eso responde tres preguntas que ningún script puede responder.

## Paso 10 · Subir los resultados a GitHub

```bash
git add -A
git commit -m "Ronda 3: 80 envíos reales y verificación en HubSpot"
git push
```

Con eso yo puedo retomar desde la sesión remota: correr el juez (ronda 4), rehacer lo que falte
(ronda 5) y redactar el informe final (ronda 6).

## Paso 11 · Limpieza, solo cuando Santiago y vos lo aprueben

Primero mirá qué se borraría (no borra nada):

```bash
python tools/limpiar_pruebas.py
```

El script muestra dos listas: los contactos que **cumplen exactamente el patrón de la prueba** y se
borrarían, y los **excluidos**, que se parecen pero no son de la prueba y no se tocan. Hoy, sin
haber corrido nada, la búsqueda ya devuelve dos contactos reales de UANDES con "_qa" en el correo:
quedan en la lista de excluidos. Si en la primera lista ves algo que no reconocés, no sigas.

Recién después, borrá de verdad:

```bash
python tools/limpiar_pruebas.py --ejecutar
```

Volvé a correr el primero para confirmar que quedaron cero. Después, avisale al equipo comercial
que la prueba terminó.

---

## Alternativa: dejar que Claude Code lo haga

Si tenés Claude Code instalado en tu computadora, podés abrir la carpeta del proyecto y pegarle el
prompt de arranque que está en la tarea de ClickUp. Los agentes del paquete están en la carpeta
`.claude/agents/` y van a correr las rondas solos. Como las rondas 0, 1 y 2 ya están hechas,
agregale al final del prompt esta línea:

> Las rondas 0, 1 y 2 ya están cerradas y su evidencia está en output/. Leé loop-workspace/estado.md,
> reconfirmá el preflight y seguí desde la ronda 3. Después de cada tanda del probador corré también
> tools/verificar_contactos.py para completar H2 y H5.

Los pasos 0 a 3 y el 6 (la llave y `DRY_RUN=0`) los tenés que hacer vos igual.

## Si algo falla

Copiá el texto completo del error y pegámelo en el chat. No intentes arreglar los scripts a mano.
Nada de lo que hace esta ronda modifica formularios, workflows ni páginas: solo envía formularios
como lo haría un visitante y lee lo que quedó en HubSpot.
