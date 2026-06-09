import subprocess
from CLI import cores
from modulos import logs
from uteis import validar_resposta
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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


def desativar(nome_servico):
    try:
        nome_servico = nome_servico.strip()
        result = subprocess.run(
            ["sc", "stop", nome_servico],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"{cores.CORES['verde']}[OK] Serviço terminado com sucesso{cores.CORES['limpo']}")
            return True

        print(f"[ERRO] {result.stderr.strip()}")
    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro ao tentar desativar um serviço (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "persistência", data_atual, erro)
        return False

def desativar_servico(nome_servico, caminho):

    print(f"""
{cores.CORES['vermelho']}[AVISO] Parar um serviço pode causar:
- Instabilidade no sistema
- Perda de conectividade de rede ou funcionalidades do Windows
- Falhas em aplicações e processos dependentes do serviço
- Comportamento inesperado do sistema operativo
Continue apenas se tiver certeza da ação.
    {cores.CORES['limpo']}
    """)

    resposta_inicial = validar_resposta.validar_resposta("Deseja parar o seguinte serviço:")

    if (resposta_inicial not in ["SIM", "S"]):
        return

    if (nome_servico.lower() in SERVICOS_CRITICOS):
        print(f"{cores.CORES['vermelho']}[ALERTA] Serviço crítico identificado.\n"
              f"Qualquer ação neste serviço pode comprometer a estabilidade do sistema operativo."
              f"{cores.CORES['limpo']}")
        resposta_final = validar_resposta.validar_resposta("Desenja realmente interromper o serviço")
        if (resposta_final not in ["SIM", "S"]):
            return
    sucesso = desativar(nome_servico)
    if (sucesso):
        logs.inserir_log("ação", "persistência", nome_servico, caminho)