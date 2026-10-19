# Parte de caza de mi partida de NevWorld

Archivo: `nevworld_633278004429261811_20261013_162358.jsonl`.

| Resultado | Valor |
| --- | --- |
| Cacerías completadas | 22 |
| Cazadores distintos | 3 |
| Presas por tipo | sheep: 21, deer: 1 |
| Construcciones abandonadas | 255 |
| Construcciones caducadas | 73 |
| Total de incidencias | 328 |
| Validaciones de las dos tablas | OK: recuentos, claves únicas, campos obligatorios y cálculo del día |

Ejemplo: event_index=109, tick=2850, villager_id=1639.0, prey_type=deer, simulation_day=0.

## Selección de campos

| Necesidad | Selección | Motivo |
| --- | --- | --- |
| Cacería completada | type == hunt_completed | Selecciona el hecho registrado. |
| Aldeano | villager_id | Identifica quién la completó. |
| Presa | prey_type | Conserva el tipo de presa. |
| Momento | tick y simulation_day | Sitúa el hecho; el día se calcula como tick // 12000 y comienza en 0. |
| Partida y evento | run_id y event_index | Permiten localizar el evento en el RAW, aunque haya líneas vacías. |

`activity` describe cambios de actividad; `food_stock` pertenece a las fotografías
del mundo y `amount_delta` a cambios de recursos. No se deduce una cantidad de comida
obtenida ni se atribuyen cambios de recursos por cercanía temporal.

## Interpretación

- Cada fila representa una cacería completada. Un mismo aldeano puede aparecer varias veces.
- Una fila sitúa el hecho en un tick; no indica el inicio ni la duración de la cacería.
- Eliminar todas las filas del RAW con algún nulo puede borrar eventos válidos, porque cada tipo utiliza campos distintos.
- Una tabla de caza vacía solo permite afirmar que no se registraron cacerías completadas; no descarta intentos.

## Ampliación: incidencias de construcción

Se seleccionan `construction_abandoned` y `construction_expired`, conservando
`type` para distinguirlos, las claves del evento, `cell_x`, `cell_y` y el día simulado.
Las incidencias registradas no tienen building_id informado; se conservan sus coordenadas.
Dos registros con las mismas coordenadas no demuestran que sean la misma obra:
el lugar puede reutilizarse. El tipo de evento tampoco explica por sí solo la causa detallada.

Adaptado de [fase02 de Elias-MN/NevWorld](https://github.com/Elias-MN/NevWorld/tree/main/fase02).
Regenerar con `python scripts/actividades/02_parte_caza.py`.

## Contraste con dos líneas originales

Evento 109: aldeano, presa y tick coinciden con el CSV.

```json
{"schema_version":2,"run_id":"20261013_162358_633278004429261811_49f7a11177cd4718b5a0c7e62dd03ab1","seed":"633278004429261811","event_index":109,"tick":2850,"type":"hunt_completed","villager_id":1639,"prey_type":"deer"}
```

Evento 177: aldeano, presa y tick coinciden con el CSV.

```json
{"schema_version":2,"run_id":"20261013_162358_633278004429261811_49f7a11177cd4718b5a0c7e62dd03ab1","seed":"633278004429261811","event_index":177,"tick":5510,"type":"hunt_completed","villager_id":1639,"prey_type":"sheep"}
```

Comprobaciones con assert: recuentos, claves únicas, campos obligatorios, día y contraste del CSV: OK.
