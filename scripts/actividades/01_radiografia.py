"""Actividad 01: reutiliza la lectura, validaciones y ficha de radiografía."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'radiografia.py'), run_name='__main__')
