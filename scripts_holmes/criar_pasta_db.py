from pathlib import Path
from time import sleep

# Vai da pasta scripts_holmes → sobe para a raiz do projeto
DIRETORIO_BASE = Path(__file__).resolve().parent.parent

# Pasta da DB dentro do projeto
FICHEIRO_DB = DIRETORIO_BASE / "base_de_dados"

def criar_ficheiro_db():
    if not FICHEIRO_DB.exists():
        print("[HOLMES] A criar pasta da base de dados e a base de dados...")
        FICHEIRO_DB.mkdir(parents=True, exist_ok=True)
        sleep(2)
        print("[OK] Pasta da base de dados pronta...")
    else:
        print("[HOLMES] A verificar pasta da base de dados")
        sleep(1)
        print("[HOLMES] A pasta da base de dados já existe")
