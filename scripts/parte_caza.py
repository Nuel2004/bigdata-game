"""Parte de caza adaptado de Elias-MN/NevWorld/fase02."""
import argparse
from pathlib import Path
import sys

# Permite ejecutar este módulo también mediante los accesos de fase02.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from radiografia import ROOT, DATASET, cargar_y_validar

BASE = ['run_id', 'event_index', 'tick']
INCIDENT_TYPES = ['construction_abandoned', 'construction_expired']


def extraer_tablas(df):
    specifications = {
        'hunts': (['hunt_completed'], [*BASE, 'villager_id', 'prey_type']),
        'construction_incidents': (INCIDENT_TYPES, [*BASE, 'type', 'cell_x', 'cell_y']),
    }
    tables = {}
    for name, (types, columns) in specifications.items():
        mask = df['type'].isin(types)
        table = df.loc[mask].reindex(columns=columns).copy()
        table['simulation_day'] = table['tick'] // 12000
        if len(table) != int(mask.sum()):
            raise ValueError(f'{name}: el número de filas no coincide con el RAW')
        if table.duplicated(['run_id', 'event_index']).any():
            raise ValueError(f'{name}: hay eventos duplicados')
        if table[columns].isna().any().any():
            raise ValueError(f'{name}: faltan campos obligatorios')
        if not (table['simulation_day'] == table['tick'] // 12000).all():
            raise ValueError(f'{name}: el día calculado es incorrecto')
        if name == 'construction_incidents' and not table['type'].isin(types).all():
            raise ValueError('Hay tipos de incidencia no permitidos')
        tables[name] = table
    return tables


def crear_ficha(df, tables, dataset):
    hunts = tables['hunts']
    incidents = tables['construction_incidents']
    counts = incidents['type'].value_counts()
    prey = ', '.join(f'{name}: {count}' for name, count in hunts['prey_type'].value_counts().items()) or 'Ninguna'
    example = 'No hay cacerías completadas registradas.'
    if not hunts.empty:
        row = hunts.iloc[0]
        example = (f"Ejemplo: event_index={row['event_index']}, tick={row['tick']}, "
                   f"villager_id={row['villager_id']}, prey_type={row['prey_type']}, "
                   f"simulation_day={row['simulation_day']}.")
    raw_incidents = df.loc[df['type'].isin(INCIDENT_TYPES)]
    has_building_id = 'building_id' in raw_incidents and raw_incidents['building_id'].notna().any()
    building_note = ('Hay incidencias con building_id informado; esta extracción conserva tipo y coordenadas.'
                     if has_building_id else 'Las incidencias registradas no tienen building_id informado; se conservan sus coordenadas.')
    return f'''# Parte de caza de mi partida de NevWorld

Archivo: `{dataset.name}`.

| Resultado | Valor |
| --- | --- |
| Cacerías completadas | {len(hunts)} |
| Cazadores distintos | {hunts['villager_id'].nunique()} |
| Presas por tipo | {prey} |
| Construcciones abandonadas | {counts.get('construction_abandoned', 0)} |
| Construcciones caducadas | {counts.get('construction_expired', 0)} |
| Total de incidencias | {len(incidents)} |
| Validaciones de las dos tablas | OK: recuentos, claves únicas, campos obligatorios y cálculo del día |

{example}

## Selección de campos

| Necesidad | Selección | Motivo |
| --- | --- | --- |
| Cacería completada | type == hunt_completed | Selecciona el hecho registrado. |
| Aldeano | villager_id | Identifica quién la completó. |
| Presa | prey_type | Conserva el tipo de presa. |
| Momento | tick y simulation_day | Sitúa el hecho; el día se calcula como tick // 12000 y comienza en 0. |
| Partida y evento | run_id y event_index | Permiten localizar el evento en el RAW, aunque haya líneas vacías. |

`activity` describe cambios de actividad; `food_stock` pertenece a las fotografías
del mundo y `amount_delta` a cambios de recursos. No se deduce una cantidad de comida
obtenida ni se atribuyen cambios de recursos por cercanía temporal.

## Interpretación

- Cada fila representa una cacería completada. Un mismo aldeano puede aparecer varias veces.
- Una fila sitúa el hecho en un tick; no indica el inicio ni la duración de la cacería.
- Eliminar todas las filas del RAW con algún nulo puede borrar eventos válidos, porque cada tipo utiliza campos distintos.
- Una tabla de caza vacía solo permite afirmar que no se registraron cacerías completadas; no descarta intentos.

## Ampliación: incidencias de construcción

Se seleccionan `construction_abandoned` y `construction_expired`, conservando
`type` para distinguirlos, las claves del evento, `cell_x`, `cell_y` y el día simulado.
{building_note}
Dos registros con las mismas coordenadas no demuestran que sean la misma obra:
el lugar puede reutilizarse. El tipo de evento tampoco explica por sí solo la causa detallada.

Adaptado de [fase02 de Elias-MN/NevWorld](https://github.com/Elias-MN/NevWorld/tree/main/fase02).
Regenerar con `python scripts/actividades/02_parte_caza.py`.
'''


def guardar_resultados(df, tables, dataset, output_dir, ficha):
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, table in tables.items():
        output = output_dir / f'{name}.csv'
        table.to_csv(output, index=False)
        print(output, '->', len(table), 'filas')
    ficha.parent.mkdir(parents=True, exist_ok=True)
    ficha.write_text(crear_ficha(df, tables, dataset), encoding='utf-8')
    print('Ficha generada:', ficha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset', type=Path, default=DATASET)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--ficha', type=Path, default=ROOT / 'reports/ficha_parte_caza.md')
    args = parser.parse_args()
    df = cargar_y_validar(args.dataset)
    tables = extraer_tablas(df)
    guardar_resultados(df, tables, args.dataset, args.output_dir, args.ficha)
    print('VALIDACIÓN DE FASE02: OK')


if __name__ == '__main__':
    main()
