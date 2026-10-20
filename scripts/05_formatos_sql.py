from pathlib import Path

import duckdb
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data/processed'
PARQUET_DIR = DATA_DIR / 'parquet'
PARQUET_DIR.mkdir(parents=True, exist_ok=True)

names = [
    'snapshots', 'resources', 'activities',
    'needs', 'social', 'buildings',
]

for name in names:
    csv_path = DATA_DIR / f'{name}.csv'
    parquet_path = PARQUET_DIR / f'{name}.parquet'

    table = pd.read_csv(csv_path)
    table.to_parquet(parquet_path, engine='pyarrow', index=False)

    print(name)
    print('  CSV:', csv_path.stat().st_size, 'bytes')
    print('  Parquet:', parquet_path.stat().st_size, 'bytes')
    
connection = duckdb.connect()

resource_query = """
    SELECT
        resource_type,
        SUM(amount_delta) AS net_change,
        COUNT(*) AS changes
    FROM read_parquet('data/processed/parquet/resources.parquet')
    GROUP BY resource_type
    ORDER BY net_change DESC
"""

resource_summary = connection.execute(
    resource_query
).fetchdf()

print('\nRECURSOS CONSULTADOS CON SQL')
print(resource_summary)



Path('reports').mkdir(exist_ok=True)

daily_query = """
    SELECT
        day,
        MAX(population) AS population,
        MAX(constructed_buildings) AS buildings,
        ROUND(AVG(wood_stock), 2) AS average_wood,
        ROUND(AVG(food_stock), 2) AS average_food
    FROM read_parquet('data/processed/parquet/snapshots.parquet')
    GROUP BY day
    ORDER BY day
"""

daily_summary = connection.execute(daily_query).fetchdf()
print('\nRESUMEN DIARIO')
print(daily_summary)

daily_summary.to_csv(
    'reports/daily_summary.csv',
    index=False,
)

connection.close()