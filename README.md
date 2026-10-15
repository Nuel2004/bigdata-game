# BigData game analysis

This project loads the raw event stream from `data/raw` and summarizes the simulation into processed CSV/JSON outputs under `data/processed`.

## Quick start

```bash
python -m pip install -r requirements.txt
python scripts/analyze_nevworld.py
```

The script reads every `.jsonl` file in `data/raw`, calculates per-event and per-tick summaries, and writes:

- `data/processed/event_counts.csv`
- `data/processed/events_by_tick.csv`
- `data/processed/summary.json`
- `data/processed/snapshot_preview.json`

## Example output

The current dataset captures a simulation with 19,640 events and a peak population of 19 villagers.

## Fase 01: radiografía de tu partida

Integración adaptada de [Elias-MN/NevWorld, fase01](https://github.com/Elias-MN/NevWorld/tree/main/fase01).
Utiliza tu archivo `nevworld_633278004429261811_20261013_162358.jsonl`.

```bash
python fase01/01_radiografia.py
# También disponible mediante el script de exploración existente:
python scripts/01_explorar.py
```

Valida los eventos, conserva la semilla y el identificador de sesión como texto,
muestra columnas y frecuencias y genera `fase01/ficha.md` con los resultados reales.
Las rutas predeterminadas se resuelven desde el proyecto, aunque ejecutes desde otra carpeta.
Puedes seleccionar otro archivo y otra ficha con `--dataset RUTA --ficha RUTA`.
La validación del orden de ticks se realiza por sesión.

En Windows, si el entorno está disponible, puedes usar
`.venv314\Scripts\python.exe` en lugar de `python`.

## Fase 02: parte de caza y ampliación

Adaptado de [Elias-MN/NevWorld, fase02](https://github.com/Elias-MN/NevWorld/tree/main/fase02),
con los resultados de tu partida.

```bash
python fase02/02_parte_caza.py
python fase02/02_parte_caza_ampliacion.py
```

Ambos comandos generan `data/processed/hunts.csv`,
`data/processed/construction_incidents.csv` y `fase02/ficha.md`.
Conservan las claves de origen y añaden `simulation_day = tick // 12000`.
Validan recuentos, duplicados, campos obligatorios y cálculo del día antes de exportar.
Los CSV se generan a partir de tu RAW; no se copian los resultados de la otra partida.

También están integrados en `python scripts/02_transformar.py`, junto con las
seis tablas existentes. Las rutas predeterminadas funcionan desde cualquier carpeta.
Los comandos de fase02 admiten `--dataset RUTA`, `--output-dir RUTA` y `--ficha RUTA`.

## Análisis de métricas

```powershell
python scripts/02_transformar.py
python scripts/03_analizar.py
```

El análisis usa las tablas procesadas de una sola partida y responde las cinco
preguntas de la guía: actividades más frecuentes y porcentajes, balance e
incrementos/reducciones de recursos, necesidades críticas, interacciones sociales
y evolución entre la primera y última fotografía del mundo.

Genera `reports/metrics_summary.csv` y los detalles en `activity_metrics.csv`,
`resource_metrics.csv`, `critical_needs.csv`, `social_interactions.csv` y
`world_evolution.csv`. `reports/README.md` explica cómo interpretar las métricas.
Las frecuencias de actividades representan cambios registrados, no tiempo dedicado.
Las rutas predeterminadas funcionan desde cualquier carpeta; admite
`--data-dir RUTA` y `--reports-dir RUTA`.
