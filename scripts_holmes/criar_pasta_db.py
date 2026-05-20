from pathlib import Path
from time import sleep

# Vai da pasta scripts → sobe para a raiz do projeto
DIRETORIO_BASE = Path(__file__).resolve().parent.parent

# Pasta da DB dentro do projeto
FICHEIRO_DB = DIRETORIO_BASE / "base_de_dados"

def criar_ficheiro_db():
    print("[HOLMES] A criar pasta da base de dados e a base de dados...")
    sleep(3)
    if not FICHEIRO_DB.exists():
        FICHEIRO_DB.mkdir(parents=True, exist_ok=True)
    print("[OK] Pasta da base de dados pronta...")
