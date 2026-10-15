# Apuntes para replicar el análisis de NevWorld

Esta guía explica cómo ejecutar el proyecto y qué hace cada paso. Los comandos están preparados para PowerShell en Windows. Ejecútalos desde la carpeta del proyecto.

## 1. Preparar el entorno

Necesitas Python instalado y el archivo de la partida en `data/raw/`. El proyecto usa actualmente:

```text
data/raw/nevworld_633278004429261811_20261013_162358.jsonl
```

Abre la carpeta del proyecto en VS Code y su terminal. Si necesitas situarte en ella manualmente:

```powershell
cd "C:\Users\manur\OneDrive\Escritorio\CE\BigData\bigdata-game"
```

Crea un entorno virtual e instala las dependencias (solo la primera vez):

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/00_comprobar_entorno.py
```

Usamos directamente el Python del entorno, así no hace falta activarlo. Si `python` no se reconoce pero tienes el lanzador de Windows, utiliza `py` en los dos primeros comandos. Si ya tienes `.venv314`, puedes sustituir `.venv` por `.venv314` en todos los ejemplos.

`requirements.txt` instala pandas, matplotlib, jupyter, pyarrow y duckdb. La comprobación debe terminar con `Entorno preparado correctamente`.

## 2. Receta rápida para repetir todo

Con el entorno preparado y el JSONL en su sitio, ejecuta estos comandos uno a uno. Si alguno falla, corrige el error antes de continuar:

```powershell
.\.venv\Scripts\python.exe scripts/01_explorar.py
.\.venv\Scripts\python.exe scripts/02_transformar.py
.\.venv\Scripts\python.exe scripts/03_analizar.py
```

El flujo es: **JSONL original → exploración y validación → tablas CSV → métricas**. Repetirlo actualiza los archivos generados y las fichas; conserva tus notas personales en este archivo, porque las fichas se regeneran.

## 3. Explorar: conocer y validar la partida

`scripts/01_explorar.py` utiliza la lógica de `scripts/radiografia.py` para leer el JSONL, mostrar sus columnas y contar los tipos de eventos. También genera `fase01/ficha.md`.

Un JSONL contiene un objeto JSON por línea. Cada línea representa un evento; pandas reúne todos los eventos en una tabla llamada `DataFrame`.

```python
df = pd.read_json(ruta, lines=True, dtype={'seed': 'string', 'run_id': 'string'})
```

- `lines=True`: lee cada línea como un JSON independiente.
- `seed` y `run_id` se conservan como texto para preservar los identificadores.
- `df['type'].value_counts()`: cuenta cuántas veces aparece cada tipo de evento.
- `len(df)`: devuelve el número de filas.

Antes de continuar, se comprueba que la tabla no esté vacía, que existan `run_id`, `event_index`, `tick` y `type` sin valores nulos, que no haya duplicados de `run_id + event_index` y que los ticks no retrocedan por sesión al ordenar los eventos por `event_index`.

Con el archivo actual, la ficha registra **19.640 eventos**, **36 columnas** y **14 tipos de evento**. El más frecuente es `villager_activity_changed`, con **10.885 registros**. Estos valores sirven como referencia para esta partida; otra partida tendrá otros resultados.

También puedes ejecutar `fase01/01_radiografia.py`: es otra entrada a la misma fase, por lo que no hace falta ejecutar ambas.

## 4. Transformar: separar los eventos en tablas

`scripts/02_transformar.py` carga y valida el original, selecciona filas por tipo de evento y guarda ocho tablas en `data/processed/`:

| Archivo | Contenido |
| --- | --- |
| `snapshots.csv` | Fotografías del mundo: población, edificios y existencias de recursos. |
| `resources.csv` | Cambios de recursos y cantidades antes/después. |
| `activities.csv` | Cambios de actividad de los aldeanos. |
| `needs.csv` | Cambios de necesidades y su estado. |
| `social.csv` | Interacciones entre aldeanos. |
| `buildings.csv` | Creaciones de edificios. |
| `hunts.csv` | Cacerías completadas. |
| `construction_incidents.csv` | Construcciones abandonadas o caducadas. |

La idea principal de la selección es:

```python
tabla = df.loc[df['type'] == 'hunt_completed',
               ['run_id', 'event_index', 'tick', 'villager_id', 'prey_type']].copy()
tabla['simulation_day'] = tabla['tick'] // 12000
tabla.to_csv('data/processed/hunts.csv', index=False)
```

Este fragmento ilustra las operaciones básicas; el script completo añade validaciones y gestiona las columnas disponibles.

- `.loc[filas, columnas]` selecciona los eventos y los campos que interesan.
- `.copy()` crea una tabla independiente.
- `//` hace división entera: el día simulado comienza en 0 y cada 12.000 ticks pasa al siguiente.
- `index=False` evita guardar el índice interno de pandas como una columna adicional.

Se conservan `run_id` y `event_index` para localizar cada evento en el original. En recursos se verifica `amount_before + amount_delta == amount_after`.

Esta ejecución también valida cacerías e incidencias y actualiza `fase02/ficha.md`. Para la partida actual se esperan **22 cacerías**, **255 construcciones abandonadas** y **73 caducadas**.

Si solo quieres repetir la fase de caza y su ampliación:

```powershell
.\.venv\Scripts\python.exe fase02/02_parte_caza.py
```

`fase02/02_parte_caza_ampliacion.py` también genera las dos tablas y la ficha. No necesitas ejecutar ambas entradas ni repetirlas después de la transformación general.

## 5. Analizar: obtener métricas

`scripts/03_analizar.py` lee las tablas procesadas. Debes ejecutar primero la transformación para que los CSV existan y correspondan a la partida que quieres estudiar.

| Resultado en `reports/` | Qué responde |
| --- | --- |
| `activity_metrics.csv` | ¿Qué cambios de actividad son más frecuentes y qué porcentaje representan? |
| `resource_metrics.csv` | ¿Cuánto aumentó y disminuyó cada recurso y cuál fue el balance? |
| `critical_needs.csv` | ¿Cuántos eventos de necesidades críticas hay por tipo? |
| `social_interactions.csv` | ¿Qué tipos de interacción aparecen y cuántas veces? |
| `world_evolution.csv` | ¿Qué cambia entre la primera y la última fotografía del mundo? |
| `metrics_summary.csv` | Resumen de seis métricas principales. |

Operaciones que conviene entender:

```python
# Frecuencias y porcentajes de actividades informadas
activities['activity'].value_counts()
activities['activity'].value_counts(normalize=True) * 100

# Sumar las variaciones de cada recurso
resources.groupby('resource_type')['amount_delta'].sum()

# Seleccionar eventos de necesidades críticas
needs.loc[needs['state'] == 'critical']

# Ordenar las fotografías para comparar la primera y la última
ordered = snapshots.sort_values(['tick', 'event_index'])
```

Los nombres `activities`, `resources`, `needs` y `snapshots` representan las tablas cargadas. Los ejemplos explican la lógica; no son un programa completo por separado.

Al interpretar los resultados:

- Contar cambios de actividad no mide el tiempo dedicado a cada actividad.
- Sumar variaciones de recursos da un balance, no las existencias finales.
- Contar eventos críticos no cuenta personas distintas ni duración del estado.
- Comparar fotografías describe los momentos registrados; no reconstruye todo lo ocurrido entre ellos.
- Una celda vacía puede ser normal: cada tipo de evento utiliza campos distintos. No elimines todas las filas con algún nulo.

## 6. Resumen general opcional del RAW

Hay otro script que resume **todos los archivos `.jsonl` de `data/raw/`**:

```powershell
.\.venv\Scripts\python.exe scripts/analyze_nevworld.py
```

Genera `event_counts.csv`, `events_by_tick.csv`, `summary.json` y `snapshot_preview.json` en `data/processed/`. Es un resumen adicional; para generar las tablas que necesita `03_analizar.py`, ejecuta `02_transformar.py`.

## 7. Repetirlo con otra partida

1. Copia el nuevo JSONL en `data/raw/` y conserva el original.
2. Cambia la constante `DATASET` en `scripts/radiografia.py` para apuntar al nuevo archivo. `02_transformar.py` importa esa constante y actualmente no tiene opción `--dataset`.
3. Ejecuta los tres comandos de la receta rápida, en orden.
4. Revisa las fichas y los CSV regenerados. Si quieres conservar los resultados anteriores, cópialos a otra carpeta antes de repetir el flujo.

Para explorar otra partida sin cambiar la constante, puedes indicar una ruta y una ficha diferentes:

```powershell
.\.venv\Scripts\python.exe scripts/01_explorar.py --dataset "data/raw/otra_partida.jsonl" --ficha "fase01/ficha_otra.md"
```

Esto solo cambia esa ejecución de exploración; no cambia el archivo que usará después la transformación general.

## 8. Errores habituales

| Mensaje o problema | Qué comprobar |
| --- | --- |
| `python` no se reconoce | Prueba `py`; si tampoco existe, instala Python y vuelve a abrir la terminal. |
| `ModuleNotFoundError` | Instala `requirements.txt` con el mismo intérprete que usas para ejecutar los scripts. |
| No se encuentra el JSONL | Comprueba el nombre, la carpeta `data/raw/` y la constante `DATASET`. |
| No se encuentra un CSV al analizar | Ejecuta primero `scripts/02_transformar.py`. |
| Eventos duplicados o ticks que retroceden | Revisa el RAW y la sesión indicada en el error antes de modificar datos. |
| Los CSV contienen varias partidas | Regenera las tablas a partir de una sola sesión antes de analizar. |

## 9. Lista de comprobación

- [ ] El entorno muestra `Entorno preparado correctamente`.
- [ ] El JSONL está en `data/raw/` y coincide con `DATASET`.
- [ ] La exploración termina sin errores y genera `fase01/ficha.md`.
- [ ] La transformación genera las ocho tablas y `fase02/ficha.md`.
- [ ] El análisis genera los seis CSV de métricas en `reports/`.
- [ ] Sé explicar qué cuenta cada métrica y qué no permite concluir.
