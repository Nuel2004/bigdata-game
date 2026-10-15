# Radiografía de mi partida de NevWorld

| Dato de mi partida | Resultado |
| --- | --- |
| Nombre del archivo JSONL | `nevworld_633278004429261811_20261013_162358.jsonl` |
| Número total de eventos | 19640 |
| Número de columnas | 36 |
| Nombres de las columnas | `schema_version`<br>`run_id`<br>`seed`<br>`event_index`<br>`tick`<br>`type`<br>`started_at_utc`<br>`building_id`<br>`building_type`<br>`cell_x`<br>`cell_y`<br>`width`<br>`height`<br>`villager_id`<br>`activity`<br>`resource_type`<br>`amount_before`<br>`amount_after`<br>`amount_delta`<br>`population`<br>`constructed_buildings`<br>`wood_stock`<br>`food_stock`<br>`gold_stock`<br>`day`<br>`prey_type`<br>`actor_id`<br>`target_id`<br>`interaction_type`<br>`topic`<br>`relationship_actor_to_target_after`<br>`relationship_target_to_actor_after`<br>`need_type`<br>`state`<br>`name`<br>`age` |
| Tipo del primer evento registrado | `simulation_started` |
| Tipo de evento más frecuente y cantidad | `villager_activity_changed`: 10885 |
| Recuento de todos los tipos de evento | `villager_activity_changed`: 10885<br>`villager_need_changed`: 3136<br>`resource_changed`: 1650<br>`world_snapshot`: 1246<br>`social_interaction`: 1228<br>`villager_drank`: 606<br>`villager_ate`: 475<br>`construction_abandoned`: 255<br>`construction_expired`: 73<br>`building_created`: 47<br>`hunt_completed`: 22<br>`villager_created`: 15<br>`simulation_started`: 1<br>`age_changed`: 1 |
| Sesión de la primera fila | `20261013_162358_633278004429261811_49f7a11177cd4718b5a0c7e62dd03ab1` |
| Semilla y esquema de la primera fila | Semilla: `633278004429261811`<br>Esquema: 2 |
| Número de sesiones | 1 |
| Tick mínimo y tick máximo | Mínimo: 0<br>Máximo: 747977 |
| Resultado de las validaciones | OK: tabla no vacía; columnas principales presentes y sin nulos; pareja run_id + event_index sin duplicados; ticks sin retrocesos por sesión al ordenar por event_index. |

### 1. ¿Qué permite afirmar el recuento? ¿Por qué el tipo más frecuente no tiene que ser el más importante?

La partida contiene 19640 eventos de 14 tipos. El más frecuente es
`villager_activity_changed`, con 10885 registros. El recuento mide apariciones,
no duración ni impacto. La creación de un aldeano o un edificio puede ser
importante aunque ocurra pocas veces.

### 2. ¿Por qué una celda vacía no significa necesariamente que el registro esté mal?

Cada tipo de evento utiliza campos distintos. Un cambio de recurso incluye
cantidades; un cambio de actividad incluye el identificador del aldeano.
Un campo ausente se interpreta según el tipo de evento y no equivale a cero.

### 3. ¿Qué sé ahora del archivo y qué pregunta necesitaría un análisis posterior?

Conocemos el tamaño, las columnas, las frecuencias, las sesiones y el intervalo
de ticks. Un análisis posterior puede estudiar cómo evoluciona la población
y si sus cambios coinciden con variaciones en las reservas de comida.

Adaptado de [fase01 de Elias-MN/NevWorld](https://github.com/Elias-MN/NevWorld/tree/main/fase01).
Regenerar con `python fase01/01_radiografia.py`.
