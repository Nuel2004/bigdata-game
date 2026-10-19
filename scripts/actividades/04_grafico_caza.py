"""Representa las cacerías completadas de la partida, agrupadas por presa."""
from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use('Agg')  # Guarda la imagen sin abrir una ventana.
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / 'data/processed/hunts.csv'
OUTPUT = ROOT / 'reports/charts/05_hunts_by_prey.png'


def cargar_cacerias(path):
    if not path.is_file():
        raise FileNotFoundError(f'No se encuentra {path}. Ejecuta scripts/02_transformar.py primero.')
    hunts = pd.read_csv(path, dtype={'run_id': 'string', 'prey_type': 'string'})
    required = ['run_id', 'event_index', 'tick', 'villager_id', 'prey_type']
    missing = [column for column in required if column not in hunts.columns]
    if missing:
        raise ValueError(f'hunts.csv: faltan columnas {missing}')
    if hunts[required].isna().any().any():
        raise ValueError('hunts.csv: hay campos obligatorios ausentes; cada cacería debe tener una presa.')
    if hunts['prey_type'].str.strip().eq('').any():
        raise ValueError('hunts.csv: hay cacerías sin presa informada.')
    if hunts['run_id'].str.strip().eq('').any() or hunts['run_id'].nunique() > 1:
        raise ValueError('hunts.csv: se requiere una sola partida con run_id informado.')
    if hunts.duplicated(['run_id', 'event_index']).any():
        raise ValueError('hunts.csv: hay eventos duplicados.')
    return hunts


def main():
    hunts = cargar_cacerias(INPUT)
    if hunts.empty:
        OUTPUT.unlink(missing_ok=True)
        print('AVISO: no hay cacerías completadas registradas. No se genera gráfico ni se puede elegir una presa predominante.')
        return

    counts = hunts['prey_type'].value_counts()
    if int(counts.sum()) != len(hunts):
        raise ValueError('El recuento por presa no coincide con el total de cacerías.')
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(8, 4))
    try:
        counts.plot.bar(color='steelblue')
        plt.title('Cacerías completadas registradas por tipo de presa')
        plt.xlabel('Tipo de presa')
        plt.ylabel('Número de cacerías completadas')
        plt.xticks(rotation=30, ha='right')
        plt.tight_layout()
        plt.savefig(OUTPUT, dpi=150)
    finally:
        plt.close()
    print(counts.to_string())
    print(f'Total representado: {int(counts.sum())}; filas de hunts.csv: {len(hunts)}')
    print(f'Imagen guardada: {OUTPUT}')


if __name__ == '__main__':
    main()
