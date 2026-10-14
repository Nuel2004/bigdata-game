import sys

import duckdb
import matplotlib
import pandas as pd
import pyarrow


print('Intérprete:', sys.executable)
print('Python:', sys.version.split()[0])
print('pandas:', pd.__version__)
print('Matplotlib:', matplotlib.__version__)
print('PyArrow:', pyarrow.__version__)
print('DuckDB:', duckdb.__version__)
print('Entorno preparado correctamente')