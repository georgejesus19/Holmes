import psutil
from uteis import validar_resposta


PROCESSOS_CRITICOS = [
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

CORES = {'vermelho':'\033[31m',
         'limpo':'\033[m'}

def terminar_processo(pid):

    print(f"""
{CORES['vermelho']}[AVISO] Interromper um processo pode causar:
- Instabilidade no sistema
- Perda de dados
- Encerramento inesperado de aplicações
Continue apenas se tiver certeza da ação.
{CORES['limpo']}""")

    resposta_inicial = validar_resposta.validar_resposta("Deseja interromper o seguinte processo:")

    if (resposta_inicial in ["SIM", "S"]):
        try:
            processo = psutil.Process(pid)
            nome = processo.name()

            if (nome in PROCESSOS_CRITICOS):
                print(f"{CORES['vermelho']}[ALERTA] Processo crítico identificado.\n"
                      f"Qualquer ação neste processo pode comprometer a estabilidade do sistema operativo."
                      f"{CORES['limpo']}")
                resposta_final = validar_resposta.validar_resposta("Desenja realmente interromper o processo")
                if (resposta_final in ["SIM", "S"]):
                    print(".... Teste concluído")
                    #processo.terminate()
                    #processo.wait(timeout=3)
                    #print("Processo terminado com sucesso")
                else:
                    return
            else:
                print(".... Teste concluído")
                # processo.terminate()
                # processo.wait(timeout=3)
                # print("Processo terminado com sucesso")
        except psutil.NoSuchProcess:
            print("ERRO: O processo em questão não existe")
        except psutil.AccessDenied:
            print("ERRO: permissão negada")
        except psutil.TimeoutExpired:
            print("INFO: O processo não respondeu ao terminate")