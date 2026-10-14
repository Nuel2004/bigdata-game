from pathlib import Path

import pandas as pd


DATASET = Path(
    'data/raw/nevworld_633278004429261811_20261013_162358.jsonl'
)

if not DATASET.exists():
    raise FileNotFoundError(
        f'No se encuentra: {DATASET.resolve()}'
    )

df = pd.read_json(DATASET, lines=True)

filas, columnas = df.shape
print('\nPRIMEROS EVENTOS')
print(df.head())

print('\nTAMAÑO')
print('Eventos:', filas)
print('Columnas:', columnas)

print('\nNOMBRES DE COLUMNA')
print(df.columns.tolist())

print('\nEVENTOS POR TIPO')
print(df['type'].value_counts())

print('\nSESIÓN')
print('run_id:', df['run_id'].iloc[0])
print('semilla:', df['seed'].iloc[0])
print('esquema:', df['schema_version'].iloc[0])
print('primer tick:', df['tick'].min())
print('último tick:', df['tick'].max())

required = [
    'run_id', 'event_index', 'tick', 'type'
]

assert not df.empty, 'El dataset está vacío'
assert all(column in df.columns for column in required), \
    'Faltan columnas principales'
assert not df.duplicated(['run_id', 'event_index']).any(), \
    'Hay eventos duplicados'

ordered = df.sort_values('event_index')
assert ordered['tick'].is_monotonic_increasing, \
    'Los ticks retroceden'

print('\nVALIDACIÓN BÁSICA: OK')