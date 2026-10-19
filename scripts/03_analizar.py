"""Calcula las métricas de la partida a partir de sus tablas procesadas."""
from pathlib import Path
import argparse

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
WORLD_COLUMNS = [
    'population', 'constructed_buildings',
    'wood_stock', 'food_stock', 'gold_stock',
]
REQUIRED = {
    'snapshots': ['run_id', 'tick', 'event_index', *WORLD_COLUMNS],
    'resources': ['run_id', 'resource_type', 'amount_delta'],
    'activities': ['run_id', 'activity'],
    'needs': ['run_id', 'state', 'need_type'],
    'social': ['run_id', 'interaction_type'],
}


def cargar_tablas(data_dir):
    tables = {}
    sessions = set()
    for name, columns in REQUIRED.items():
        path = data_dir / f'{name}.csv'
        if not path.is_file():
            raise FileNotFoundError(f'No se encuentra {path}. Ejecuta scripts/02_transformar.py primero.')
        table = pd.read_csv(path, dtype={'run_id': 'string'})
        missing = [column for column in columns if column not in table.columns]
        if missing:
            raise ValueError(f'{path.name}: faltan columnas {missing}')
        if table['run_id'].isna().any():
            raise ValueError(f'{path.name}: hay registros sin run_id')
        sessions.update(table['run_id'].unique())
        tables[name] = table
    if len(sessions) > 1:
        raise ValueError('Los CSV contienen varias partidas. Genera las tablas de una sola sesión antes de analizar.')
    return tables


def calcular_metricas(tables):
    snapshots = tables['snapshots']
    resources = tables['resources']
    activities = tables['activities']
    needs = tables['needs']
    social = tables['social']

    # Los porcentajes usan solo registros con actividad informada, no tiempo.
    activity_counts = activities['activity'].value_counts()
    activity_proportions = activities['activity'].value_counts(normalize=True)
    activity_percent = (activity_proportions * 100).round(1)
    activity_report = pd.DataFrame({'count': activity_counts, 'percent': activity_percent})

    # El balance neto no equivale a las existencias finales.
    resource_groups = resources.groupby('resource_type')
    delta_groups = resource_groups['amount_delta']
    resource_balance = delta_groups.sum()
    resource_balance = resource_balance.sort_values(ascending=False)
    gains = resources[resources['amount_delta'] > 0]
    spending = resources[resources['amount_delta'] < 0].copy()
    spending['amount_delta'] = spending['amount_delta'].abs()
    resource_report = pd.DataFrame({
        'net_change': resource_balance,
        'increases': gains.groupby('resource_type')['amount_delta'].sum(),
        'reductions': spending.groupby('resource_type')['amount_delta'].sum(),
    }).fillna(0).sort_values('net_change', ascending=False)

    critical_needs = needs[needs['state'] == 'critical']
    critical_counts = critical_needs['need_type'].value_counts()
    interaction_counts = social['interaction_type'].value_counts()

    ordered_snapshots = snapshots.sort_values(['tick', 'event_index'])
    last = None
    evolution_rows = []
    if not ordered_snapshots.empty:
        first = ordered_snapshots.iloc[0]
        last = ordered_snapshots.iloc[-1]
        for column in WORLD_COLUMNS:
            evolution_rows.append({
                'metric': column, 'first': first[column], 'last': last[column],
                'change': last[column] - first[column],
            })
    evolution = pd.DataFrame(evolution_rows, columns=['metric', 'first', 'last', 'change'])
    summary = pd.DataFrame([
        {'metric': 'events_activity', 'value': len(activities)},
        {'metric': 'events_resource', 'value': len(resources)},
        {'metric': 'critical_needs', 'value': len(critical_needs)},
        {'metric': 'social_interactions', 'value': len(social)},
        {'metric': 'final_population', 'value': None if last is None else last['population']},
        {'metric': 'final_buildings', 'value': None if last is None else last['constructed_buildings']},
    ])
    return {
        'activity_metrics': activity_report.rename_axis('activity').reset_index(),
        'resource_metrics': resource_report.rename_axis('resource_type').reset_index(),
        'critical_needs': critical_counts.rename_axis('need_type').reset_index(name='count'),
        'social_interactions': interaction_counts.rename_axis('interaction_type').reset_index(name='count'),
        'world_evolution': evolution,
        'metrics_summary': summary,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=ROOT / 'data/processed')
    parser.add_argument('--reports-dir', type=Path, default=ROOT / 'reports')
    args = parser.parse_args()
    tables = cargar_tablas(args.data_dir)
    reports = calcular_metricas(tables)
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    titles = ['ACTIVIDADES Y PORCENTAJES', 'BALANCE, INCREMENTOS Y REDUCCIONES DE RECURSOS',
              'NECESIDADES CRÍTICAS', 'INTERACCIONES SOCIALES', 'EVOLUCIÓN DEL MUNDO', 'RESUMEN']
    for title, (name, report) in zip(titles, reports.items()):
        print('\n' + title)
        print(report.to_string(index=False) if not report.empty else 'No hay registros para esta métrica.')
        report.to_csv(args.reports_dir / f'{name}.csv', index=False)
    sessions = set().union(*(set(t['run_id']) for t in tables.values()))
    session = next(iter(sessions), 'Sin registros')
    notes = f'''# Métricas de mi partida

Sesión: `{session}`.

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
'''
    (args.reports_dir / 'README.md').write_text(notes, encoding='utf-8')
    print('\nInformes guardados en:', args.reports_dir)


if __name__ == '__main__':
    main()
