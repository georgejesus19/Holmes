import subprocess
import sys
import importlib.util
from time import sleep

DEPENDENCIAS = {
    "psutil": "psutil",
    "requests": "requests",
    "pyfiglet": "pyfiglet",
    "python-dotenv": "dotenv"
}

def esta_instalado(modulo):
    return importlib.util.find_spec(modulo) is not None

def install_dependencies():
    print("[HOLMES] A verificar dependências...")

    sleep(1)

    for pacote, modulo in DEPENDENCIAS.items():

        if esta_instalado(modulo):
            print(f"[OK] {pacote} já está instalado.")
            continue

        print(f"[HOLMES] A instalar {pacote}...")

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pacote]
            )
            print(f"[OK] {pacote} instalado com sucesso.")

        except subprocess.CalledProcessError:
            print(f"[ERRO] Falha ao instalar {pacote}")

    print("[OK] Processo de dependências concluído.")