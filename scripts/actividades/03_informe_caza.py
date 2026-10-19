"""Actividad 03: métricas de cacerías y cambios de comida de una partida."""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]


def cargar_tabla(name, fields):
    path = ROOT / f'data/processed/{name}.csv'
    if not path.is_file():
        raise FileNotFoundError(f'Falta {path}; genera primero las tablas procesadas.')
    table = pd.read_csv(path, dtype={'run_id': 'string'})
    required = ['run_id', 'event_index', *fields]
    missing = [c for c in required if c not in table.columns]
    if missing:
        raise ValueError(f'{name}: faltan columnas {missing}')
    if table[required].isna().any().any():
        raise ValueError(f'{name}: hay campos obligatorios ausentes')
    for column in table[required].select_dtypes(include=['object', 'string']).columns:
        if table[column].astype('string').str.strip().eq('').any():
            raise ValueError(f'{name}: hay valores vacíos en {column}')
    if table.duplicated(['run_id', 'event_index']).any():
        raise ValueError(f'{name}: hay eventos duplicados')
    return table


def main():
    hunts = cargar_tabla('hunts', ['prey_type', 'simulation_day', 'tick'])
    resources = cargar_tabla('resources', ['resource_type', 'amount_delta'])
    snapshots = cargar_tabla('snapshots', ['tick', 'food_stock'])
    sessions = set().union(*(set(t['run_id']) for t in [hunts, resources, snapshots]))
    if len(sessions) > 1:
        raise ValueError('Las tablas mezclan partidas distintas')
    assert (hunts['simulation_day'] == hunts['tick'] // 12000).all(), 'Días incoherentes'
    counts = hunts['prey_type'].value_counts()
    percentages = hunts['prey_type'].value_counts(normalize=True) * 100
    days = hunts['simulation_day'].value_counts().sort_index()
    print(f'Total de cacerías completadas registradas: {len(hunts)}')
    if hunts.empty:
        print('No hay cacerías completadas registradas.')
    print('\nRecuentos por presa:\n', counts.to_string())
    print('\nPorcentajes por presa:\n', percentages.round(1).to_string())
    print('\nRecuentos por día observado con cacerías:\n', days.to_string())
    food = resources[resources['resource_type'] == 'food']
    # Primero filtrar y después sumar, como en el tema de métricas.
    gains_table = food[food['amount_delta'] > 0]
    spending = food[food['amount_delta'] < 0].copy()
    spending['amount_delta'] = spending['amount_delta'].abs()
    gains = gains_table['amount_delta'].sum()
    reductions = spending['amount_delta'].sum()
    net = food['amount_delta'].sum()
    if food.empty:
        print('AVISO: no hay cambios de comida registrados; las sumas cero no indican existencias cero.')
    assert counts.sum() == len(hunts), 'Suma por presa incorrecta'
    assert days.sum() == len(hunts), 'Suma por día incorrecta'
    assert abs(float(gains - reductions - net)) < 0.000001, 'Balance incoherente'
    if not hunts.empty:
        assert abs(float(percentages.sum()) - 100) < 0.000001, 'Porcentajes incoherentes'
    summary = pd.DataFrame([
        {'metric': 'hunt_events', 'value': len(hunts)},
        {'metric': 'food_change_events', 'value': len(food)},
        {'metric': 'food_gains', 'value': gains},
        {'metric': 'food_reductions', 'value': reductions},
        {'metric': 'food_net_change', 'value': net},
    ])
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    summary.to_csv(reports / 'hunting_summary.csv', index=False)
    print('\n', summary.to_string(index=False))
    print('ASSERT: sumas por presa y día, balance y porcentajes: OK')
    ordered = snapshots.sort_values(['tick', 'event_index'])
    if ordered.empty:
        snapshot_note = 'No hay fotografías; no se calcula diferencia ni se accede a iloc.'
    else:
        first, last = ordered.iloc[0], ordered.iloc[-1]
        snapshot_note = (f"Primera fotografía: tick {first['tick']}, comida {first['food_stock']}; "
                         f"última: tick {last['tick']}, comida {last['food_stock']}; "
                         f"diferencia {last['food_stock'] - first['food_stock']}.")
        if len(ordered) == 1:
            snapshot_note += ' Solo hay una fotografía; la diferencia cero no demuestra estabilidad.'
    leaders = ', '.join(map(str, counts[counts == counts.max()].index)) if not counts.empty else 'ninguna (sin registros)'
    ficha = f'''# Informe de caza de mi partida

RAW: `nevworld_633278004429261811_20261013_162358.jsonl`.
Partida: `{next(iter(sessions), 'sin registros')}`.

## Decisiones

| Pregunta | Tabla y columnas | Operación y motivo |
| --- | --- | --- |
| Total de cacerías | hunts | len: cada fila es una cacería completada |
| Recuento por presa | hunts.prey_type | value_counts: frecuencia de categorías |
| Porcentaje por presa | hunts.prey_type | value_counts(normalize=True) * 100: reparto del total |
| Recuento por día | hunts.simulation_day | value_counts().sort_index(): orden cronológico |
| Cambios de comida | resources.resource_type y amount_delta | filtrar food y sumar positivos, magnitudes negativas y todos los cambios |

## Resultados

Total: {len(hunts)} cacerías. Cada fila registra un hecho completado; el denominador de los porcentajes es ese total.

```text
Recuentos por presa:
{counts.to_string()}

Porcentajes (un decimal):
{percentages.round(1).to_string()}

Recuentos por día con registros:
{days.to_string()}

Resumen:
{summary.to_string(index=False)}
```

Validaciones: columnas, nulos, cadenas vacías, claves únicas y partida común: OK.
Assert: suma por presa = suma por día = {len(hunts)}; incrementos − reducciones = balance; porcentajes sin redondear ≈ 100 si hay cacerías: OK.
No se añaden días sin registros: esta tabla no determina todo el periodo observado.
Si no hay cacerías, el total es cero y no existe una presa predominante; si no hay cambios de comida, las sumas cero no demuestran ausencia de comida.

## Cinco conclusiones

1. La presa con mayor recuento es {leaders}; el máximo es {int(counts.max()) if not counts.empty else 0} registros. Se incluyen todas las categorías empatadas si las hay.
2. Los porcentajes son de cacerías completadas: dividen el recuento de cada presa entre {len(hunts)} eventos, no entre aldeanos ni unidades de tiempo.
3. El día con más registros no demuestra mayor tiempo de caza: faltan inicio, fin o duración de cada intento.
4. El balance neto {net} es variación, no existencias finales; haría falta el stock inicial del mismo intervalo y un registro completo de cambios.
5. Los incrementos {gains} no pueden atribuirse todos a la caza: se necesita una causa explícita o un identificador que vincule cada cambio de comida con su cacería y la cantidad producida.

## Ampliación: fotografías

{snapshot_note}
El balance de eventos de comida es {net}. No se fuerza igualdad: las fotografías y los cambios pueden cubrir intervalos distintos. Una discrepancia no prueba un error por sí sola.
'''
    (reports / 'ficha_informe_caza.md').write_text(ficha, encoding='utf-8')
    print(snapshot_note)


if __name__ == '__main__':
    main()
