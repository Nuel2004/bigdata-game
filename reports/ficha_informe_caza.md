# Informe de caza de mi partida

RAW: `nevworld_633278004429261811_20261013_162358.jsonl`.
Partida: `20261013_162358_633278004429261811_49f7a11177cd4718b5a0c7e62dd03ab1`.

## Decisiones

| Pregunta | Tabla y columnas | Operación y motivo |
| --- | --- | --- |
| Total de cacerías | hunts | len: cada fila es una cacería completada |
| Recuento por presa | hunts.prey_type | value_counts: frecuencia de categorías |
| Porcentaje por presa | hunts.prey_type | value_counts(normalize=True) * 100: reparto del total |
| Recuento por día | hunts.simulation_day | value_counts().sort_index(): orden cronológico |
| Cambios de comida | resources.resource_type y amount_delta | filtrar food y sumar positivos, magnitudes negativas y todos los cambios |

## Resultados

Total: 22 cacerías. Cada fila registra un hecho completado; el denominador de los porcentajes es ese total.

```text
Recuentos por presa:
prey_type
sheep    21
deer      1

Porcentajes (un decimal):
prey_type
sheep    95.5
deer      4.5

Recuentos por día con registros:
simulation_day
0     5
3     2
4     1
7     2
8     2
9     3
10    1
33    1
34    1
39    1
48    1
56    1
57    1

Resumen:
            metric  value
       hunt_events   22.0
food_change_events  723.0
        food_gains 1353.0
   food_reductions 1025.0
   food_net_change  328.0
```

Validaciones: columnas, nulos, cadenas vacías, claves únicas y partida común: OK.
Assert: suma por presa = suma por día = 22; incrementos − reducciones = balance; porcentajes sin redondear ≈ 100 si hay cacerías: OK.
No se añaden días sin registros: esta tabla no determina todo el periodo observado.
Si no hay cacerías, el total es cero y no existe una presa predominante; si no hay cambios de comida, las sumas cero no demuestran ausencia de comida.

## Cinco conclusiones

1. La presa con mayor recuento es sheep; el máximo es 21 registros. Se incluyen todas las categorías empatadas si las hay.
2. Los porcentajes son de cacerías completadas: dividen el recuento de cada presa entre 22 eventos, no entre aldeanos ni unidades de tiempo.
3. El día con más registros no demuestra mayor tiempo de caza: faltan inicio, fin o duración de cada intento.
4. El balance neto 328.0 es variación, no existencias finales; haría falta el stock inicial del mismo intervalo y un registro completo de cambios.
5. Los incrementos 1353.0 no pueden atribuirse todos a la caza: se necesita una causa explícita o un identificador que vincule cada cambio de comida con su cacería y la cantidad producida.

## Ampliación: fotografías

Primera fotografía: tick 600, comida 4.0; última: tick 747600, comida 321.0; diferencia 317.0.
El balance de eventos de comida es 328.0. No se fuerza igualdad: las fotografías y los cambios pueden cubrir intervalos distintos. Una discrepancia no prueba un error por sí sola.
