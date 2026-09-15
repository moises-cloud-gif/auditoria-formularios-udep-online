# Diseño del loop

## Por qué siete rondas y no un bucle abierto

La tentación en una auditoría de 80 casos es dejar al agente iterando hasta que "quede bien". Eso
produce dos fallas conocidas: gasta presupuesto sin converger, y —peor— aprende que declarar la
ronda terminada es más barato que ejecutarla. Por eso acá el trabajo es un **pipeline con un solo
bucle acotado**, y la única parte que repite es la que puede fallar por causas transitorias.

```
  R0 preflight ──FALLA──► ALTO, no se ejecuta nada más
        │ PASA
        ▼
  R1 inventarios (3 agentes en paralelo)
        │
        ▼
  R2 clasificación A/B/C/D
        │
        ▼
  ┌─► R3 probador de envíos ──► R4 juez ──PASA──► R6 informe
  │                                │
  │                             REVISAR
  │                                ▼
  └──────────────────────────  R5 remediador
       (máx. 2 vueltas)
```

## Guardas de parada

Cuatro, y basta con que una se dispare.

| Guarda | Valor | Qué evita |
|---|---|---|
| Preflight en FALLA | corte inmediato | Auditar sin acceso |
| Pasadas del probador | **3** como máximo | Bucle infinito de reintentos |
| Pasadas del remediador | **2** como máximo | Remediación que nunca converge |
| Sin progreso | si dos veredictos seguidos traen los mismos huecos, se cierra | Girar sin avanzar |

Cerrar por tope **no es un fracaso**: es una salida válida. El informe se emite igual, con la lista
de huecos abiertos y su causa, y Moisés decide.

## Verificación, en este orden

Primero programática, después juez, humano al final. Es deliberado: un juez que revisa antes de que
el script cuente termina justificando lo que lee.

1. **`tools/verificar_evidencia.py`** — no opina, cuenta. Falla si hay menos de 40 páginas
   recorridas, menos de 40 formularios leídos, menos de 80 instancias, alguna instancia sin captura
   en disco, algún `hs_object_id` que no existe en el portal, correos repetidos, o todo en seco.
2. **`juez-evidencia`** — modelo en el asiento del revisor, **sin permiso de escritura**. No puede
   dar PASA si el verificador falló.
3. **Moisés** — revisa el informe, aporta criterio y aprueba la limpieza.

## El antipatrón que este diseño ataca

Un loop que corre sus tres rondas, escribe conclusiones prolijas y nunca abrió una página ni
consultó el portal. Las tres defensas concretas:

- El preflight guarda la respuesta cruda de la API y una captura real antes de permitir avanzar.
- Cada fila de evidencia exige una captura que **existe en disco** y un `hs_object_id` que
  **responde 200 en el portal**. Ninguna de las dos se puede escribir de memoria.
- El verificador contrasta lo reportado contra lo hallado: si el agente dice 80 y en el portal hay
  60 contactos de prueba, la ronda falla.

## Presupuesto

La ronda 3 es el 70% del costo. Corre por tandas de 10 páginas y verifica el lado HubSpot entre
tandas: si la primera no crea contactos, las otras siete tampoco, y no tiene sentido ensuciar la
base con 80 registros inútiles.
