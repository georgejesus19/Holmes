import subprocess
from CLI import cores
from modulos import logs
from uteis import validar_resposta
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

TAREFAS_CRITICAS = [
    r"\microsoft\windows\windowsupdate",
    r"\microsoft\windows\updateorchestrator",
    r"\microsoft\windows\taskscheduler",
    r"\microsoft\windows\systemrestore",
    r"\microsoft\windows\windows defender",
    r"\microsoft\windows\defrag",
    r"\microsoft\windows\diskcleanup",
    r"\microsoft\windows\customer experience improvement program",
    r"\microsoft\windows\application experience",
    r"\microsoft\windows\memorydiagnostic",
    r"\microsoft\windows\shell",
    r"\microsoft\windows\time synchronization",
    r"\microsoft\windows\registry"
]

def desativar_tarefa(nome_tarefa):
    try:
        result = subprocess.run(
            ["schtasks", "/Change", "/TN", nome_tarefa, "/Disable"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"{cores.CORES['verde']}[OK] Tarefa desativada com sucesso{cores.CORES['limpo']}")
            return True

        print(f"[ERRO] Falha ao desativar: {nome_tarefa}")

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro ao tentar desativar uma tarefa agendada (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "persistência", data_atual, erro)
        return False

def desativar_tarefa_agendada(nome_tarefa, caminho):

    print(f"""
{cores.CORES['vermelho']}[AVISO] Desativar uma tarefa agendada pode causar:
- Falhas em atualizações do sistema
- Perda de funcionalidades automáticas
- Instabilidade em serviços do Windows
Continue apenas se tiver certeza da ação.
{cores.CORES['limpo']}
""")

    resposta_inicial = validar_resposta.validar_resposta("Deseja desativar a seguinte tarefa agendada:")

    if (resposta_inicial not in ["SIM", "S"]):
        print("... Teste concluído")
        return

    nome_tarefa = nome_tarefa.strip()

    for caminho in TAREFAS_CRITICAS:
        if (nome_tarefa.lower().startswith(caminho)):
            print(f"{cores.CORES['vermelho']}[ALERTA] Tarefa crítica identificada.\n"
                  f"Qualquer ação nesta tarefa pode comprometer o funcionamento correto do sistema operativo."
                  f"{cores.CORES['limpo']}")
            resposta_final = validar_resposta.validar_resposta("Desenja realmente desativar a tarefa")

            if (resposta_final not in ["SIM", "S"]):
                return

    sucesso = desativar_tarefa(nome_tarefa)
    if (sucesso):
        logs.inserir_log("ação", "persistência", nome_tarefa, caminho, data_atual)