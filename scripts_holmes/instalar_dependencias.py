import subprocess
import sys
import importlib.util
from time import sleep
from CLI import cores

DEPENDENCIAS = {
    "psutil": "psutil",
    "requests": "requests",
    "pyfiglet": "pyfiglet",
    "python-dotenv": "dotenv"
}

rotulo = f"{cores.CORES['azul']}HOLMES{cores.CORES['limpo']}"
def esta_instalado(modulo):
    return importlib.util.find_spec(modulo) is not None

def install_dependencies():
    print(f"[{rotulo}] A verificar dependências...")

    sleep(1)

    for pacote, modulo in DEPENDENCIAS.items():

        if esta_instalado(modulo):
            print(f"[{rotulo}] {pacote} já está instalado.")
            continue

        print(f"[{rotulo}] A instalar {pacote}...")

        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pacote]
            )
            print(f"[{rotulo}] {pacote} instalado com sucesso.")
            sleep(1)

        except subprocess.CalledProcessError:
            print(f"[{rotulo}] {cores.CORES['vermelho']}Falha ao instalar{cores.CORES['limpo']} {pacote}")

    print(f"[{rotulo}] Processo de dependências concluído.")
    sleep(1)