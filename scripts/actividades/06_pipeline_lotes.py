# hashlib viene con Python: sha256 calcula la huella del archivo.
from hashlib import sha256
# Path permite trabajar con rutas de archivos y carpetas.
from pathlib import Path
# Importamos de time un contador para medir duraciones en segundos.
from time import perf_counter

import pandas as pd


RAW_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
REPORTS_DIR = Path('reports')
# Creamos las carpetas de salida si no existen.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)

# Buscamos los JSONL de NevWorld y ordenamos sus nombres; * es la parte variable.
files = sorted(RAW_DIR.glob('nevworld_*.jsonl'))
# Si no hay archivos, detenemos el programa con un mensaje.
if not files:
    raise FileNotFoundError('No hay JSONL en data/raw')

# Lo siguiente prepara el programa para medir cuánto tarda en ejecutarse, almacenar los datos y registrar información sobre los archivos procesados:

start = perf_counter() #Inicia un cronómetro para medir el tiempo de ejecución.

frames = [] # Lista para almacenar los DataFrames.
manifest = [] # Lista para registrar información sobre cada archivo procesado.

# Segundo bloque: añádelo debajo del anterior. Revisamos un archivo por vuelta.
for path in files:
    # Leemos los bytes y obtenemos su huella como texto hexadecimal.
    checksum = sha256(path.read_bytes()).hexdigest()
    # lines=True indica que cada línea contiene un evento JSON independiente.
    frame = pd.read_json(path, lines=True)

    # Aceptamos tablas no vacías donde todas las filas declaran la versión 2.
    # eq(2) compara cada valor y all() exige que todos cumplan.
    valid_schema = (
        'schema_version' in frame.columns
        and not frame.empty
        and frame['schema_version'].eq(2).all()
    )

    # append añade una ficha: nombre, tamaño en bytes, filas, huella y estado.
    manifest.append({
        'file': path.name,
        'bytes': path.stat().st_size,
        'rows': len(frame),
        'sha256': checksum,
        # Elegimos la etiqueta según el resultado de la comprobación.
        'status': 'accepted' if valid_schema else 'rejected',
    })

    # Solo conservamos las tablas compatibles para combinarlas.
    if valid_schema:
        # Guardamos el origen de cada fila para poder rastrearla después.
        frame['source_file'] = path.name
        frames.append(frame)
        
# Tercer bloque: fuera del for, sin sangría.
# No podemos unir tablas si no se ha aceptado ninguna.
if not frames:
    raise ValueError('Ningún archivo utiliza el esquema 2')

# Unimos las filas; ignore_index crea un nuevo índice de pandas.
events = pd.concat(frames, ignore_index=True)

# Contamos repeticiones de la pareja que identifica un evento en una partida.
duplicates = events.duplicated(
    ['run_id', 'event_index']
).sum()

# Nos detenemos para investigar duplicados, en lugar de borrarlos.
if duplicates:
    raise ValueError(
        f'Se detectaron {duplicates} eventos duplicados'
    )

# Ordenamos por partida y, dentro de ella, por número de evento.
events = events.sort_values(
    ['run_id', 'event_index']
)

# Cuarto bloque: guardamos los eventos combinados en Parquet.
# Esto no regenera los CSV de recursos, necesidades y demás tablas.
events.to_parquet(
    OUTPUT_DIR / 'all_events.parquet',
    index=False,
)

# Convertimos la lista de fichas en una tabla y guardamos el inventario.
pd.DataFrame(manifest).to_csv(
    REPORTS_DIR / 'manifest.csv',
    index=False,
)

# Tiempo transcurrido hasta aquí; no incluye escribir el informe siguiente.
elapsed = perf_counter() - start

# Creamos un resumen de una fila para esta ejecución.
# nunique cuenta partidas distintas; round redondea los segundos.
run_report = pd.DataFrame([{
    'files_found': len(files),
    'files_accepted': len(frames),
    'sessions': events['run_id'].nunique(),
    'events': len(events),
    'seconds': round(elapsed, 3),
}])

# Guardamos el resumen sin el índice interno de pandas.
run_report.to_csv(
    REPORTS_DIR / 'pipeline_run.csv',
    index=False,
)

# Mostramos el mismo resumen como texto en la consola.
print(run_report.to_string(index=False))