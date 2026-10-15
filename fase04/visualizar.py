from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DATA_DIR = Path('data/processed')
CHARTS_DIR = Path('reports/charts')
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

snapshots = pd.read_csv(DATA_DIR / 'snapshots.csv')
activities = pd.read_csv(DATA_DIR / 'activities.csv')
needs = pd.read_csv(DATA_DIR / 'needs.csv')
social = pd.read_csv(DATA_DIR / 'social.csv')