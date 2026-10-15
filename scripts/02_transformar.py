#Importa Path, una clase de Python para trabajar con rutas de archivos y carpetas.
from pathlib import Path

# En lugar de escribir rutas como simples textos:
# "data/raw/archivo.jsonl"
# puedes tratarlas como objetos:
# Path("data/raw/archivo.jsonl")
# Esto facilita operaciones como crear carpetas, comprobar si existen archivos, construir rutas, etc.


#Pandas se utiliza para trabajar con datos en forma de tablas mediante objetos llamados DataFrame
import pandas as pd
from radiografia import ROOT, DATASET, cargar_y_validar
from parte_caza import extraer_tablas, crear_ficha

#Aquí guardamos en la variable DATASET la ruta del archivo que vamos a analizar.

#Aquí definimos otra ruta:
OUTPUT_DIR = ROOT / 'data/processed'

#Esta línea crea la carpeta: data/processed si todavía no existe.
# parents=True -> crea también las carpetas superiores si hacen falta.
# exist_ok=True -> si la carpeta ya existe, no des error.
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# Pandas lee el archivo JSONL y lo convierte en un DataFrame.
# lines=True -> indica que cada línea del archivo es un JSON independiente.
df = cargar_y_validar(DATASET)


def event_table(event_type, columns):

    # lista con las columnas que siempre queremos y además las que hayas pasado a la función.
    selected = ['run_id', 'event_index', 'tick', *columns]

    # list comprehension, Podríamos escribirla de forma más larga así:
    # available = []

    # for column in selected:
    #     if column in df.columns:
    #         available.append(column)

    # Esta parte evita errores si alguna columna no existe.

    available = [
        column for column in selected
        if column in df.columns
    ]


    # Aquí hacemos dos operaciones al mismo tiempo: Filtrar filas y seleccionar columnas.
    # "dame las filas cuyo type sea igual al evento que busco, pero únicamente con las columnas de available"
    # Así que aunque el DataFrame original tenga 30 columnas, nuestra tabla podría quedarse con solo 4, las que hemos indicado.
    # .copy() se usa para crear una copia independiente de los datos que acabas de seleccionar,
    # sin .copy(), Pandas a veces puede tratar esa selección como una especie de vista del DataFrame original, no como una tabla
    # totalmente independiente, pudiendo ocasionar conflictos si modificamos algo.
    table = df.loc[
        df['type'] == event_type,
        available,
    ].copy()


    if not table.empty:
        # Creamos una nueva columna simulation_day y su valor es la división
        # entre table['tick'] y 12000, que nos permite sacar cuantos días han transcurrido
        # En NevWorld 12000 ticks es un día.
        table['simulation_day'] = table['tick'] // 12000

    return table


# Creamos las tablas usando la anterior función indicando el tipo de evento que queremos.
# obtener y las columnas que nos puedan interesar.
tables = {
    'snapshots': event_table('world_snapshot', [
        'population', 'constructed_buildings',
        'wood_stock', 'food_stock', 'gold_stock', 'day',
    ]),
    'resources': event_table('resource_changed', [
        'resource_type', 'amount_before',
        'amount_after', 'amount_delta',
    ]),
    'activities': event_table('villager_activity_changed', [
        'villager_id', 'activity', 'resource_type',
    ]),
    'needs': event_table('villager_need_changed', [
        'villager_id', 'need_type', 'state',
    ]),
    'social': event_table('social_interaction', [
        'actor_id', 'target_id', 'interaction_type', 'topic',
        'relationship_actor_to_target_after',
        'relationship_target_to_actor_after',
    ]),
    'buildings': event_table('building_created', [
        'building_id', 'building_type',
        'cell_x', 'cell_y', 'width', 'height',
    ]),
}

# Fase02: extraer y validar cacerías e incidencias antes de exportar.
fase02_tables = extraer_tablas(df)
tables.update(fase02_tables)

# Lo siguiente es una prueba para ver si los datos son correctos
resources = tables['resources']

# Se comprueba fila a fila si los cálculos coinciden
if not resources.empty:
    valid = (
        resources['amount_before']
        + resources['amount_delta']
        == resources['amount_after']
    )
    if not valid.all():
        raise ValueError('Hay cambios de recursos incoherentes')
    # valid.all() si todo es true
    # comprueba que todas las filas cumplan la fórmula before + delta = after. Si alguna no la cumple, detén el programa mostrando el mensaje "Hay cambios de recursos incoherentes".



    # tables.items() devuelve parejas:
  # "resources", tabla_recursos
  # "births", tabla_nacimientos
  # "deaths", tabla_muertes
# Por lo que en cada vuelta, "name" es el nombre de la tabla y "table" el dataframe correspondiente
for name, table in tables.items():
    # Esto crea la ruta donde se guardará el archivo.
    output = OUTPUT_DIR / f'{name}.csv'

    # convierte el DataFrame en un archivo CSV y lo guarda en output
    # index=False significa que no quieres que Pandas guarde el índice interno del DataFrame.
    # Sin ello, podriamos obtener una salida como: ",amount_before", en lugar de amount_before,
    table.to_csv(output, index=False)

    # Muestra por pantalla el nombre de la tabla y cuántas filas tiene.
    print(name, '->', len(table), 'filas')

ficha = ROOT / 'fase02/ficha.md'
ficha.parent.mkdir(parents=True, exist_ok=True)
ficha.write_text(crear_ficha(df, fase02_tables, DATASET), encoding='utf-8')
print('Ficha generada:', ficha)
