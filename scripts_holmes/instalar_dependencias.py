import subprocess
import sys
import importlib.util
from time import sleep

DEPENDENCIAS = ["psutil", "requests", "pyfiglet", "python-dotenv"]

def esta_instalado(dependencia):
    return importlib.util.find_spec(dependencia) is not None

def install_dependencies():
    print("[HOLMES] A verificar dependências...")

    sleep(1)

    for dependencia in DEPENDENCIAS:

        if esta_instalado(dependencia):
            print(f"[OK] {dependencia} já está instalado.")
            continue

        print(f"[HOLMES] A instalar {dependencia}...")

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", dependencia]
            )
            print(f"[OK] {dependencia} instalado com sucesso.")
        except subprocess.CalledProcessError:
            print(f"[ERRO] Falha ao instalar {dependencia}")
    print("[OK] Processo de dependências concluído.")