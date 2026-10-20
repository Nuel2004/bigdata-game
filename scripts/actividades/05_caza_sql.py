from pathlib import Path

import duckdb
import pandas as pd

ruta_csv = Path("data/processed/hunts.csv")

hunts = pd.read_csv(ruta_csv)

print(hunts.head())

assert "prey_type" in hunts.columns, "Falta la columna prey_type"

assert hunts["prey_type"].notna().all(), "Hay cacerías sin presa informada"

assert hunts["prey_type"].str.strip().ne("").all(), "Hay presas con texto vacío"

carpeta_parquet = Path("data/processed/parquet")
carpeta_parquet.mkdir(parents=True, exist_ok=True)

ruta_parquet = carpeta_parquet / "hunts.parquet"
hunts.to_parquet(ruta_parquet, engine="pyarrow", index=False)

print("Tamaño del CSV:", ruta_csv.stat().st_size, "bytes")
print("Tamaño del Parquet:", ruta_parquet.stat().st_size, "bytes")

connection = duckdb.connect()

hunt_query = """
    SELECT 
        prey_type,
        COUNT(*) AS hunt_count
    FROM read_parquet('data/processed/parquet/hunts.parquet')
    GROUP BY prey_type
    ORDER BY hunt_count DESC
"""

resultado = connection.execute(hunt_query).fetchdf()
print(resultado)

assert resultado["hunt_count"].sum() == len(hunts), "Los recuentos no coinciden"

carpeta_reports = Path("reports")
carpeta_reports.mkdir(parents=True, exist_ok=True)

ruta_resultado = carpeta_reports / "hunts_by_prey_sql.csv"
resultado.to_csv(ruta_resultado, index=False)

connection.close()