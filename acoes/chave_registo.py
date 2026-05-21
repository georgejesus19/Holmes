import subprocess
from uteis import validar_resposta

CORES = {'vermelho':'\033[31m',
         'limpo':'\033[m'}

import subprocess

def remover_entrada(chave, subchave, entrada):
    try:
        caminho_completo = f"{chave}\\{subchave}"

        result = subprocess.run(
            ["reg", "delete", caminho_completo, "/v", entrada, "/f"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] Entrada removida: {entrada}")
        else:
            print(f"[ERRO] {result.stderr.strip()}")

    except Exception as ex:
        print(f"[ERRO] inesperado: {ex}")

def remover_entrada_chave_registo(chave, subchave, entrada):

    print(f"""{CORES['vermelho']}[AVISO] Remover uma entrada de arranque do registo pode causar:
- Impedimento de programas iniciarem automaticamente com o Windows
- Perda de funcionalidades de software instalado
- Instabilidade em aplicações dependentes dessa entrada
- Comportamento inesperado no arranque do sistema
Continue apenas se tiver certeza da ação.
        {CORES['limpo']}""")

    resposta = validar_resposta.validar_resposta("Deseja remover esta entrada?")

    if resposta not in ["SIM", "S"]:
        return

    if chave.upper() == "HKLM":

        print(f"""{CORES['vermelho']}[ALERTA CRÍTICO] Entrada de sistema (HKLM) detetada.
Esta alteração afeta TODOS os utilizadores do Windows.
- Pode afetar o arranque do sistema
- Pode afetar serviços críticos
- Pode causar instabilidade grave no sistema operativo
Continue apenas se tiver total certeza.
        {CORES['limpo']}""")

        resposta_final = validar_resposta.validar_resposta("Confirmar remoção crítica?")
        if resposta_final not in ["SIM", "S"]:
            return
    #remover_entrada(chave, subchave, entrada)
    #print("[INFO] entrada removida")
    print("... Teste concluído")