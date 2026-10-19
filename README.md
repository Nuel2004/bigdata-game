# Análisis de mi partida de NevWorld

## Estructura

```text
bigdata-game/
├── scripts/                # Transformación, análisis y visualización del temario
│   └── actividades/        # Los cuatro ejercicios
├── data/
│   ├── raw/                # Registro original, sin modificar
│   └── processed/          # Tablas generadas desde el RAW
├── reports/                # Fichas y métricas, sin copias duplicadas
│   └── charts/             # Los cinco gráficos PNG
├── apuntes/                # Explicaciones personales; ignoradas por Git
└── notebooks/              # Cuaderno de análisis
```

## Ejecutar

Desde bigdata-game con `.venv` activado:

```powershell
python scripts/01_explorar.py
python scripts/02_transformar.py
python scripts/03_analizar.py
python scripts/04_visualizar.py
```

Ejercicios:

```powershell
python scripts/actividades/01_radiografia.py
python scripts/actividades/02_parte_caza.py
python scripts/actividades/03_informe_caza.py
python scripts/actividades/04_grafico_caza.py
```

La exploración y la actividad 01 reutilizan scripts/radiografia.py. La transformación general reutiliza scripts/parte_caza.py para cacerías e incidencias. Son módulos compartidos, no copias de las implementaciones.

## Resultados de las actividades

| Ejercicio | Resultados |
| --- | --- |
| 01 | reports/ficha_radiografia.md |
| 02 | data/processed/hunts.csv, construction_incidents.csv y reports/ficha_parte_caza.md |
| 03 | reports/hunting_summary.csv y reports/ficha_informe_caza.md |
| 04 | reports/charts/05_hunts_by_prey.png y reports/ficha_grafico_caza.md |

Los gráficos generales están en reports/charts y el resumen general en reports/metrics_summary.csv. La actividad 02 añade a su ficha el contraste de dos líneas originales; ejecútala después de la transformación si necesitas esa ficha completa.

Origen: data/raw/nevworld_633278004429261811_20261013_162358.jsonl. Se conserva el RAW; los CSV procesados se regeneran mediante los scripts. Los recuentos describen eventos registrados, no duración ni causas.

Los antiguos directorios fase01, fase02, fase04 y NevWorld se consolidaron en esta estructura. Los entornos de respaldo .venv314 y .venv-python315-backup se conservan; el entorno activo es .venv con Python 3.14.