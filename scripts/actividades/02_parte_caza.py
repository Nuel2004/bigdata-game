"""Actividad 02: extrae cacerías e incidencias sin modificar el RAW."""
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from radiografia import ROOT, DATASET, cargar_y_validar
from parte_caza import crear_ficha


def event_table(df, types, fields):
    columns = ['run_id', 'event_index', 'tick', *fields]
    mask = df['type'].isin(types)
    table = df.loc[mask].reindex(columns=columns).copy()
    table['simulation_day'] = table['tick'] // 12000
    assert len(table) == int(mask.sum()), 'El recuento no coincide con el RAW'
    assert not table.duplicated(['run_id', 'event_index']).any(), 'Eventos duplicados'
    assert table[columns].notna().all().all(), 'Faltan campos obligatorios'
    for column in table.select_dtypes(include=['object', 'string']).columns:
        assert table[column].astype('string').str.strip().ne('').all(), f'Campo vacío: {column}'
    assert (table['simulation_day'] == table['tick'] // 12000).all(), 'Día incorrecto'
    return table


def main():
    df = cargar_y_validar(DATASET)
    tables = {
        'hunts': event_table(df, ['hunt_completed'], ['villager_id', 'prey_type']),
        'construction_incidents': event_table(
            df, ['construction_abandoned', 'construction_expired'], ['type', 'cell_x', 'cell_y']),
    }
    output_dir = ROOT / 'data/processed'
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        output = output_dir / f'{name}.csv'
        table.to_csv(output, index=False)
        print(f'{output}: {len(table)} filas')
    # Releer el CSV comprueba también la exportación, no solo la tabla en memoria.
    exported = pd.read_csv(output_dir / 'hunts.csv', dtype={'run_id': 'string'})
    comparisons = []
    raw_lines = DATASET.read_text(encoding='utf-8').splitlines()
    import json
    original = {(e['run_id'], e['event_index']): (line, e)
                for line in raw_lines if line.strip() for e in [json.loads(line)]}
    for _, row in exported.head(2).iterrows():
        line, event = original[(row['run_id'], row['event_index'])]
        assert event['type'] == 'hunt_completed'
        assert all(row[c] == event[c] for c in ['villager_id', 'prey_type', 'tick'])
        comparisons.append(f"Evento {row['event_index']}: aldeano, presa y tick coinciden con el CSV.\n\n```json\n{line}\n```")
    if exported.empty:
        comparisons.append('CSV vacío con cabeceras; no hay filas que contrastar con cacerías originales.')
    ficha = crear_ficha(df, tables, DATASET)
    ficha += '\n## Contraste con dos líneas originales\n\n' + '\n\n'.join(comparisons)
    ficha += '\n\nComprobaciones con assert: recuentos, claves únicas, campos obligatorios, día y contraste del CSV: OK.\n'
    (ROOT / 'reports').mkdir(exist_ok=True)
    (ROOT / 'reports/ficha_parte_caza.md').write_text(ficha, encoding='utf-8')
    print('VALIDACIONES Y CONTRASTE DEL CSV: OK')


if __name__ == '__main__':
    main()
