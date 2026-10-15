"""Ejecuta la fase02 completa, incluida la ampliación de construcción."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/parte_caza.py'), run_name='__main__')
