from pathlib import Path

# Vai da pasta scripts → sobe para a raiz do projeto
DIRETORIO_BASE = Path(__file__).resolve().parent.parent

# Pasta da DB dentro do projeto
FICHEIRO_DB = DIRETORIO_BASE / "base_de_dados"

def criar_ficheiro_db():
    if not FICHEIRO_DB.exists():
        FICHEIRO_DB.mkdir(parents=True, exist_ok=True)
