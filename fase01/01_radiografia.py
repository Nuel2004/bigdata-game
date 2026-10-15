"""Ejecuta la radiografía adaptada a este proyecto."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).resolve().parents[1] / 'scripts/radiografia.py'), run_name='__main__')
