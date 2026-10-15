"""Radiografía adaptada de https://github.com/Elias-MN/NevWorld/tree/main/fase01."""
from pathlib import Path
import argparse
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / 'data/raw/nevworld_633278004429261811_20261013_162358.jsonl'


def cargar_y_validar(dataset):
    if not dataset.is_file():
        raise FileNotFoundError(f'No se encuentra: {dataset}')
    df = pd.read_json(dataset, lines=True, dtype={'seed': 'string', 'run_id': 'string'})
    if df.empty:
        raise ValueError('El dataset está vacío')
    required = ['run_id', 'event_index', 'tick', 'type']
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f'Faltan columnas principales: {missing}')
    if df[required].isna().any().any():
        raise ValueError('Hay valores vacíos en las columnas principales')
    if df.duplicated(['run_id', 'event_index']).any():
        raise ValueError('Hay eventos duplicados')
    for run_id, run in df.groupby('run_id'):
        if not run.sort_values('event_index')['tick'].is_monotonic_increasing:
            raise ValueError(f'Los ticks retroceden en la sesión {run_id}')
    return df


def crear_ficha(df, dataset):
    counts = df['type'].value_counts()
    first = df.iloc[0]
    rows = [
        ('Nombre del archivo JSONL', f'`{dataset.name}`'),
        ('Número total de eventos', len(df)),
        ('Número de columnas', len(df.columns)),
        ('Nombres de las columnas', '<br>'.join(f'`{c}`' for c in df.columns)),
        ('Tipo del primer evento registrado', f"`{first['type']}`"),
        ('Tipo de evento más frecuente y cantidad', f'`{counts.index[0]}`: {counts.iloc[0]}'),
        ('Recuento de todos los tipos de evento', '<br>'.join(f'`{n}`: {v}' for n, v in counts.items())),
        ('Sesión de la primera fila', f"`{first['run_id']}`"),
        ('Semilla y esquema de la primera fila', f"Semilla: `{first.get('seed', 'No disponible')}`<br>Esquema: {first.get('schema_version', 'No disponible')}"),
        ('Número de sesiones', df['run_id'].nunique()),
        ('Tick mínimo y tick máximo', f"Mínimo: {df['tick'].min()}<br>Máximo: {df['tick'].max()}"),
        ('Resultado de las validaciones', 'OK: tabla no vacía; columnas principales presentes y sin nulos; pareja run_id + event_index sin duplicados; ticks sin retrocesos por sesión al ordenar por event_index.'),
    ]
    table = '\n'.join(f'| {name} | {value} |' for name, value in rows)
    return f'''# Radiografía de mi partida de NevWorld

| Dato de mi partida | Resultado |
| --- | --- |
{table}

### 1. ¿Qué permite afirmar el recuento? ¿Por qué el tipo más frecuente no tiene que ser el más importante?

La partida contiene {len(df)} eventos de {len(counts)} tipos. El más frecuente es
`{counts.index[0]}`, con {counts.iloc[0]} registros. El recuento mide apariciones,
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
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=DATASET)
    parser.add_argument('--ficha', type=Path, default=ROOT / 'fase01/ficha.md')
    args = parser.parse_args()
    df = cargar_y_validar(args.dataset)
    ficha = crear_ficha(df, args.dataset)
    print('VALIDACIÓN BÁSICA: OK')
    print('\nPRIMEROS EVENTOS\n', df.head())
    print('\n', ficha)
    args.ficha.parent.mkdir(parents=True, exist_ok=True)
    args.ficha.write_text(ficha, encoding='utf-8')
    print('Ficha generada:', args.ficha)


if __name__ == '__main__':
    main()
