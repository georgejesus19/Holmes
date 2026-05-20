from pathlib import Path

# Vai da pasta scripts → sobe para a raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Pasta da DB dentro do projeto
DB_FOLDER = BASE_DIR / "base_de_dados"

def criar_ficheiro_db():
    DB_FOLDER.mkdir(parents=True, exist_ok=True)
