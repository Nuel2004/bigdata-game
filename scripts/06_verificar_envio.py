from pathlib import Path
from hashlib import sha256

# Esta ruta se interpreta desde la raíz de bigdata-game.
patha = Path('data/intercambio/envio/partida_A.jsonl')
pathb = Path('data/intercambio/envio/partida_B.jsonl')
# La huella representa los bytes del archivo que acabamos de leer.
huella = sha256(patha.read_bytes()).hexdigest()
print(patha.name, patha.stat().st_size, huella)
huella = sha256(pathb.read_bytes()).hexdigest()
print(pathb.name, pathb.stat().st_size, huella)