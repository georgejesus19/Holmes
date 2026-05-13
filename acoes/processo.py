import psutil
from uteis import validar_resposta


PROCESSOS_CRITICOS = ["explorer.exe", "winlogon.exe",
                      "csrss.exe"   , "services.exe",
                        "lsass.exe" ,  "svchost.exe"]

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
    resposta = validar_resposta.validar_resposta("Deseja interromper o seguinte processo:")

    if (resposta in ["SIM", "S"]):
        try:
            processo = psutil.Process(pid)
            processo.terminate()

            processo.wait(timeout=3)
            print("Processo terminado com sucesso")

        except psutil.NoSuchProcess:
            print("ERRO: O processo em questão não existe")
        except psutil.AccessDenied:
            print("ERRO: permissão negada")
        except psutil.TimeoutExpired:
            print("INFO: O processo não respondeu ao terminate, forçando encerramento...")

            try:
                processo.kill()
                print("Processo terminado com sucesso")
            except Exception as e:
                print(f"ERRO Falha ao forçar encerramento: {e}")
        except Exception as e:
            print(f"Erro: {e}")