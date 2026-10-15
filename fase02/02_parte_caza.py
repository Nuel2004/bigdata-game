"""Genera las tablas de caza e incidencias y la ficha de esta partida."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/parte_caza.py'), run_name='__main__')
