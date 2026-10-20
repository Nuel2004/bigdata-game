from pathlib import Path
from hashlib import sha256
import pandas as pd

# Esta ruta se interpreta desde la raíz de bigdata-game.
patha = Path('data/intercambio/recibido/partida_A.jsonl')
pathb = Path('data/intercambio/recibido/partida_B.jsonl')
ruta = Path("data/intercambio/recibido/referencia.txt")
# La huella representa los bytes del archivo que acabamos de leer.
huellaA = sha256(patha.read_bytes()).hexdigest()
huellaB = sha256(pathb.read_bytes()).hexdigest()

contenido = ruta.read_text(encoding="utf-8")
lineas = contenido.splitlines()
resA = ""
resB = ""
if lineas[0].split()[-1] == huellaA:
    
    resA ="No hay cambios en A"
else:
    resA = "Hay cambios en A"

if lineas[1].split()[-1] == huellaB:
    resB = "No hay cambios en B"
else:
    resB = "Hay cambios en B"
    
print("Huella A:")
print("Esperado:" + huellaA)
print("Recibido:" + lineas[0])
print("Resultado:" + resA)

print("Huella B:")
print("Esperado:" + huellaB)
print("Recibido:" + lineas[1])
print("Resultado:" + resB)