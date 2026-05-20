import subprocess
import sys

# Lista de dependências externas do Holmes
DEPENDENCIES = ["psutil", "requests", "pyfiglet"]

def install_dependencies():
    print("[HOLMES] A instalar dependências...")
    for package in DEPENDENCIES:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"[OK] {package} instalado com sucesso.")
        except subprocess.CalledProcessError:
            print(f"[ERRO] Falha ao instalar {package}")

    print("[OK] Todas as dependências foram instaladas.")
