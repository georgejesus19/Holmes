import psutil
from CLI import cores
from modulos import logs
from uteis import validar_resposta
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

PROCESSOS_CRITICOS = [
    "System Idle Process",
    "explorer.exe",
    "winlogon.exe",
    "csrss.exe",
    "services.exe",
    "lsass.exe",
    "svchost.exe",
    "smss.exe",
    "wininit.exe",
    "lsaiso.exe",
    "spoolsv.exe",
    "taskhostw.exe",
    "dwm.exe",
    "logonui.exe",
    "system",
    "fontdrvhost.exe",
    "runtimebroker.exe"]

def terminar_processo(pid, caminho, modulo="processos"):

    print(f"""
{cores.CORES['vermelho']}[AVISO] Interromper um processo pode causar:
- Instabilidade no sistema
- Perda de dados
- Encerramento inesperado de aplicações
Continue apenas se tiver certeza da ação.
{cores.CORES['limpo']}""")

    resposta_inicial = validar_resposta.validar_resposta("Deseja interromper o seguinte processo?")

    if resposta_inicial not in ["SIM", "S"]:
        return

    try:
        processo = psutil.Process(pid)
        nome = processo.name()
        filhos = processo.children(recursive=True)

        if nome in PROCESSOS_CRITICOS:
            print(f"""
{cores.CORES['vermelho']}[ALERTA] Processo crítico identificado.
Qualquer ação neste processo pode comprometer a estabilidade do sistema operativo.
{cores.CORES['limpo']}""")

            resposta_final = validar_resposta.validar_resposta("Deseja realmente interromper o processo?")

            if resposta_final not in ["SIM", "S"]:
                return

        if filhos:
            print(f"""
{cores.CORES['amarelo']}[INFO] Este processo tem {len(filhos)} processos filhos.
{cores.CORES['limpo']}""")

            resposta_tree = validar_resposta.validar_resposta("Deseja terminar também os processos filhos")

            kill_tree = resposta_tree in ["SIM", "S"]
        else:
            kill_tree = False

        if kill_tree:
            for filho in filhos:
                try:
                    filho.terminate()
                except Exception as e:
                    print(
                        f"{cores.CORES['vermelho']}"
                        f"[ERRO] Falha ao terminar filho PID: {filho.pid} (Verificar logs de erro)"
                        f"{cores.CORES['limpo']}"
                    )
                    erro = f"PID filho: {filho.pid} | {type(e).__name__}: {e}"
                    logs.inserir_log_erro("erro","processos",data_atual, erro)
                    continue

        processo.terminate()
        processo.wait(timeout=3)
        print(f"{cores.CORES['verde']}[OK] Processo terminado com sucesso {cores.CORES['limpo']}")
        logs.inserir_log("ação", modulo, nome, caminho, data_atual)

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro ao tentar terminar o processo (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "processos", data_atual, erro)