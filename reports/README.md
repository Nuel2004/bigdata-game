# Métricas de mi partida

Sesión: `20261013_162358_633278004429261811_49f7a11177cd4718b5a0c7e62dd03ab1`.

Los resultados se regeneran con `python scripts/03_analizar.py` después de
`python scripts/02_transformar.py`. Cada CSV de esta carpeta contiene una métrica
o un grupo de métricas; `metrics_summary.csv` conserva las seis cifras del resumen.

## Interpretación y límites

- Actividades: recuentos y porcentajes de cambios con actividad informada; no miden duración ni aldeanos distintos.
- Recursos: suma de variaciones, incrementos y reducciones por separado. El balance no es el stock final y el signo no identifica la causa.
- Necesidades críticas: eventos con estado `critical`; una persona puede aparecer varias veces y no se calcula cuánto duró ese estado.
- Interacciones: frecuencia por tipo; no demuestra causalidad ni cuenta personas distintas.
- Evolución: diferencia entre la primera y última fotografía disponibles, ordenadas por tick y event_index. No reconstruye cambios intermedios ni garantiza cubrir toda la partida. Sin fotografías, las cifras finales quedan vacías.

## Comprobación de comprensión

Python aporta `for`, `if`, `len`, `print`, booleanos y diccionarios.
Pandas aporta `DataFrame`, `Series`, `value_counts`, `groupby`, `sum`,
`sort_values`, `.iloc` y `to_csv`.

Ejemplo: el porcentaje de `moving` responde qué fracción de los cambios de
actividad informados corresponde a ese valor. No permite concluir qué porcentaje
del tiempo caminaron los aldeanos.

Adaptado de [Analizar y obtener métricas](https://marnev.vercel.app/teoria/nevworld-big-data/analizar-metricas), según el texto proporcionado.
