from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / 'data/processed'
CHARTS_DIR = ROOT / 'reports/charts'
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

snapshots = pd.read_csv(DATA_DIR / 'snapshots.csv')
activities = pd.read_csv(DATA_DIR / 'activities.csv')
needs = pd.read_csv(DATA_DIR / 'needs.csv')
social = pd.read_csv(DATA_DIR / 'social.csv')


# Validar antes de dibujar: no mezclar partidas ni ocultar campos ausentes.
sessions = set()
for name, table, fields in [
    ('snapshots', snapshots, ['tick', 'wood_stock', 'food_stock', 'gold_stock']),
    ('activities', activities, ['activity']),
    ('needs', needs, ['state', 'need_type']),
    ('social', social, ['interaction_type']),
]:
    required = ['run_id', 'event_index', *fields]
    missing = [column for column in required if column not in table.columns]
    if missing:
        raise ValueError(f'{name}: faltan columnas {missing}')
    if table[required].isna().any().any():
        raise ValueError(f'{name}: hay valores necesarios ausentes')
    if table.duplicated(['run_id', 'event_index']).any():
        raise ValueError(f'{name}: hay eventos duplicados')
    for column in table[required].select_dtypes(include=['object', 'string']).columns:
        if table[column].str.strip().eq('').any():
            raise ValueError(f'{name}: hay valores vacíos en {column}')
    sessions.update(table['run_id'].unique())
if len(sessions) > 1:
    raise ValueError('Los CSV deben corresponder a una misma partida.')


def hay_datos(data, filename):
    if data.empty:
        (CHARTS_DIR / filename).unlink(missing_ok=True)
        print(f'AVISO: no hay registros para {filename}; se omite el gráfico.')
        return False
    return True

# Ordena las fotografías por tiempo antes de unir sus valores.
ordered = snapshots.sort_values(['tick', 'event_index'])

# Crea una figura: figsize indica ancho y alto en pulgadas.
if hay_datos(ordered, '01_resources_timeline.png'):
    plt.figure(figsize=(10, 5))

    # Dibuja cada línea: primer argumento = eje X, segundo = eje Y.
    # label asigna el nombre que aparecerá en la leyenda.
    plt.plot(ordered['tick'], ordered['wood_stock'], label='Madera')
    plt.plot(ordered['tick'], ordered['food_stock'], label='Comida')
    plt.plot(ordered['tick'], ordered['gold_stock'], label='Oro')

    # Escribe el título y los nombres de los ejes.
    plt.title('Evolución de los recursos')
    plt.xlabel('Tick')
    plt.ylabel('Cantidad disponible')

    # Muestra los nombres asignados con label.
    plt.legend()

    # Ajusta los márgenes para reducir solapamientos y recortes.
    plt.tight_layout()

    # Guarda la imagen PNG en reports/charts.
    plt.savefig(CHARTS_DIR / '01_resources_timeline.png')

    # Cierra la figura actual; el PNG guardado se conserva.
    plt.close()

# pandas cuenta cuántas veces aparece cada actividad.
activity_counts = activities['activity'].value_counts()

if hay_datos(activity_counts, '02_activities.png'):
    plt.figure(figsize=(10, 5))

    # plot.bar dibuja una barra por categoría; color elige su color.
    activity_counts.plot.bar(color='steelblue')
    plt.title('Cambios de actividad registrados')
    plt.xlabel('Actividad')
    plt.ylabel('Número de eventos')

    # Gira las etiquetas 45 grados y las alinea a la derecha.
    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '02_activities.png')
    plt.close()

critical = needs[needs['state'] == 'critical']
critical_counts = critical['need_type'].value_counts()

# Crea una figura de 7 por 4 pulgadas.
if hay_datos(critical_counts, '03_critical_needs.png'):
    plt.figure(figsize=(7, 4))
    critical_counts.plot.bar(color='darkorange')
    plt.title('Necesidades que alcanzaron estado crítico')
    plt.xlabel('Necesidad')
    plt.ylabel('Número de eventos')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '03_critical_needs.png')
    plt.close()


interaction_counts = social['interaction_type'].value_counts()

# Crea una figura de 8 por 4 pulgadas.
if hay_datos(interaction_counts, '04_social_interactions.png'):
    plt.figure(figsize=(8, 4))
    interaction_counts.plot.bar(color='seagreen')
    plt.title('Tipos de interacción social')
    plt.xlabel('Interacción')
    plt.ylabel('Número de eventos')
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    plt.savefig(CHARTS_DIR / '04_social_interactions.png')
    plt.close()
print('Gráficos revisados y guardados en:', CHARTS_DIR)
