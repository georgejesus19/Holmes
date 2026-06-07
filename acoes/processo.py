import psutil
from CLI import cores
from modulos import logs
from uteis import validar_resposta


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
                except Exception:
                    pass

        processo.terminate()
        processo.wait(timeout=3)

        print(f"{cores.CORES['verde']}[OK] Processo terminado com sucesso {cores.CORES['limpo']}")
        logs.inserir_log("ação", modulo, nome, caminho)

    except psutil.NoSuchProcess:
        print("ERRO: O processo em questão não existe")

    except psutil.AccessDenied:
        print("ERRO: permissão negada")

    except psutil.TimeoutExpired:
        print("INFO: O processo não respondeu ao terminate")