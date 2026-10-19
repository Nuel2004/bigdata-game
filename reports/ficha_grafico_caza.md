# El parte de caza, de un vistazo

Origen: `data/processed/hunts.csv`, derivado de `nevworld_633278004429261811_20261013_162358.jsonl`.
Partida: `20261013_162358_633278004429261811_49f7a11177cd4718b5a0c7e62dd03ab1`.

## Decisiones iniciales

1. Cada barra representa un tipo de presa y cuenta los eventos de cacería completada registrados con esa presa.
2. El eje vertical muestra el número de cacerías completadas registradas, en unidades de eventos.
3. Las presas son categorías sin un orden continuo: unas barras permiten comparar sus frecuencias; una línea sugeriría una continuidad entre categorías que no existe.

Título: **Cacerías completadas registradas por tipo de presa**.

## Comprobación con la actividad 03

| Presa | Recuento del informe 03 | Altura de la barra |
| --- | --- | --- |
| sheep | 21 | 21 |
| deer | 1 | 1 |
| Total | 22 | 22 |

Las cantidades representadas suman las 22 filas de hunts.csv. El PNG se ha abierto y revisado: título, ejes y etiquetas se leen completos.
Se validan campos obligatorios, presa no vacía, claves únicas y una sola partida antes de contar. Una fila sin presa provoca un error; no se trata como una tabla vacía.
Si no hay filas, el script avisa, omite el gráfico y elimina la imagen anterior de su ruta de salida para que no se confunda con un resultado actual.

## Tres frases finales

1. **Observación:** `sheep` es la presa con más registros, 21 cacerías completadas, frente a 1 de `deer`; no hay empate en el máximo.
2. **Límite:** el gráfico cuenta eventos completados, pero no contiene la duración de los intentos ni la cantidad de comida producida por cada presa.
3. **Pregunta pendiente:** ¿qué presa aporta más comida por unidad de tiempo de caza?, para responder necesitaríamos la duración de cada intento y la comida obtenida vinculada a su cacería.

Ejecución desde bigdata-game: `python scripts/actividades/04_grafico_caza.py`.
Imagen: `reports/charts/05_hunts_by_prey.png`.
