import subprocess
from uteis import validar_resposta

SERVICOS_CRITICOS = [
    "wininit",
    "csrss",
    "services",
    "lsass",
    "smss",
    "winlogon",
    "windefend",
    "securityhealthservice",
    "wscsvc",
    "dhcp",
    "dnscache",
    "nlasvc",
    "eventlog",
    "sysmain",
    "plugplay",
    "power",
    "spooler",
    "schedule",
    "cryptsvc"
]

CORES = {'vermelho':'\033[31m',
         'limpo':'\033[m'}

def desativar(nome_servico):
    try:
        nome_servico = nome_servico.strip()
        result = subprocess.run(
            ["sc", "stop", nome_servico],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"[OK] Serviço parado: {nome_servico}")
        else:
            print(f"[ERRO] {result.stderr.strip()}")
    except Exception as ex:
        print(f"[ERRO]: erro inesperado {ex}")

def desativar_servico(nome_servico):

    print(f"""
{CORES['vermelho']}[AVISO] Parar um serviço pode causar:
- Instabilidade no sistema
- Perda de conectividade de rede ou funcionalidades do Windows
- Falhas em aplicações e processos dependentes do serviço
- Comportamento inesperado do sistema operativo
Continue apenas se tiver certeza da ação.
    {CORES['limpo']}
    """)

    resposta_inicial = validar_resposta.validar_resposta("Deseja parar o seguinte serviço:")

    if (resposta_inicial in ["SIM", "S"]):

        if (nome_servico.lower() in SERVICOS_CRITICOS):
            print(f"{CORES['vermelho']}[ALERTA] Serviço crítico identificado.\n"
                  f"Qualquer ação neste serviço pode comprometer a estabilidade do sistema operativo."
                  f"{CORES['limpo']}")
            resposta_final = validar_resposta.validar_resposta("Desenja realmente interromper o serviço")
            if (resposta_final in ["SIM", "S"]):
                print("... Teste concluído")
                #desativar(nome_servico)
                return
            else:
                print("... Teste concluído")
                return
        print("... Teste concluído")
        #desativar(nome_servico)

