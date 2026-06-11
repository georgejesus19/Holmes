from pathlib import Path
from time import sleep
from CLI import cores
# Vai da pasta scripts_holmes → sobe para a raiz do projeto
DIRETORIO_BASE = Path(__file__).resolve().parent.parent

# Pasta da DB dentro do projeto
FICHEIRO_DB = DIRETORIO_BASE / "base_de_dados"
rotulo = f"{cores.CORES['azul']}HOLMES{cores.CORES['limpo']}"

def criar_ficheiro_db():
    if not FICHEIRO_DB.exists():
        print(f"[{rotulo}] A criar pasta da base de dados e a base de dados...")
        FICHEIRO_DB.mkdir(parents=True, exist_ok=True)
        sleep(2)
        print(f"[{rotulo}] Pasta da base de dados pronta...")
    else:
        print(f"[{rotulo}] A verificar pasta da base de dados")
        sleep(1)
        print(f"[{rotulo}] A pasta da base de dados já existe")
