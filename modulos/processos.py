import os
import psutil
from CLI import cores
from modulos import logs
from uteis import verificar_assinatura_digital
from uteis import obter_hash
from uteis import normalizar_caminho
from uteis import caminho_raiz
from uteis import carregar_lista
from uteis import pontos_assinatura
from uteis import criar_string
from uteis import calcular_score
from uteis import atribuir_risco

# =========================
# FUNÇÃO AUXILIAR
# =========================
def verificar_dados_caminho(caminho, tipos_assinatura):

    dados = {
        'caminho': caminho,
        'hash': '',
        'assinatura_digital': '',
        'status': ''
    }

    try:
        resultado = logs.consultar_binario(caminho)
        if resultado:
            return resultado

        if caminho in ['Acesso negado ou processo terminado', '', 'Registry']:
            dados['assinatura_digital'] = 'Ignorado (Sistema)'
            dados['hash'] = 'Ignorado (Sistema)'
            dados['status'] = 'Sistema'

        else:
            assinatura_binario = verificar_assinatura_digital.verificar_assinatura(caminho)

            dados['hash'] = obter_hash.obter_hash(caminho)
            dados['status'] = assinatura_binario
            dados['assinatura_digital'] = tipos_assinatura.get(assinatura_binario, "Assinatura desconhecida")

        logs.inserir_binario(dados['caminho'], dados['hash'], dados['assinatura_digital'], dados['status'])

        return dados

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro ao consultar os dados do binário (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "processos", erro)

        return {
            'caminho': caminho,
            'hash': "Erro",
            'assinatura_digital': "Erro na análise",
            'status': "Erro"
        }

# =========================
# FUNÇÕES DE PRINCIPAIS.
# =========================
def obter_processos():
    """
    Método obter_processos, serve para obter todos os processoas.
    :return: Devolve uma lista de todos os processos.txt (programas em execução)
    """
    try:
        os.system("cls")
        print("Processos Analisados: \n")

        processos = list()
        temp = dict()
        tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                            'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                            'UnknownError': 'Erro na verificação da assinatura digital'}

        lista = carregar_lista.carregar_lista("listas/blacklist.txt")

        for process in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'exe']):
            try:
                # Tenta atribuir o caminho do executável.
                try:
                    caminho = process.exe()
                # Em caso de exceções atribui uma string a variavel.
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    caminho = "Acesso negado ou processo terminado"

                resultado_consulta = verificar_dados_caminho(caminho, tipos_assinatura)
                # Atribui o valor a  cada chave do dicionário
                temp['pid'] = process.pid  # pid (process id)
                temp['ppid'] = process.ppid()  # ppid (parent process id)
                temp['nome'] = process.name()
                temp['caminho'] = resultado_consulta['caminho']
                temp['utilizador'] = process.username()
                temp['hash'] = resultado_consulta['hash']
                temp['assinatura'] = resultado_consulta['assinatura_digital']
                temp['status'] = resultado_consulta['status']
                temp['pontuacao'] = 0
                temp['risco'] = ''

                item = calcular_score_processos(lista, temp.copy())
                temp['pontuacao'] = item[0]['pontuacao']
                temp['risco'] = item[0]['risco']

                motivo = criar_string.criar_string_motivo(item[1])

                processos_copia = temp.copy()
                processos.append(processos_copia)
                mostrar_processos([processos_copia], item[1])

                if (logs.consultar_processo(temp['pid'])):
                    logs.update_processo(temp['pid'], temp['utilizador'], temp['pontuacao'], temp['risco'], motivo)
                else:
                    id_binario = logs.consultar_binario(temp['caminho'])
                    logs.inserir_processo(temp['pid'], temp['ppid'], temp['nome'], temp['utilizador'],
                                          temp['pontuacao'],
                                          temp['risco'], motivo, id_binario["id"])
            except Exception as e:
                print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a análise de um processo (verificar logs de erro){cores.CORES['limpo']}")
                erro =  f"{type(e).__name__}: {e}"
                logs.inserir_log_erro("erro", "processos", erro)
                continue

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a análise (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "processos", erro)
        return


def calcular_score_processos(ficheiro, processo):

    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    try:
        caminho_processo = normalizar_caminho.normalizar(processo['caminho'])

        score, motivo = pontos_assinatura.pontos_assinatura(processo['status'])
        dados_score['pontuacao'] += score

        if processo['status'] not in ["Valid", "Sistema"]:
            motivos.append(motivo)

        if caminho_raiz.verificar_caminho_raiz(caminho_processo):
            dados_score['pontuacao'] += 25
            motivos.append("Programa na raiz do disco")

        score_local, motivos_locais = calcular_score.calcular_score_auxiliar(
            ficheiro,
            processo['nome'],
            caminho_processo)

        dados_score['pontuacao'] += score_local['pontuacao']
        motivos.extend(motivos_locais)

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante o cálculo de score (verificar logs de erro){cores.CORES['limpo']}")
        logs.inserir_log_erro("erro","processos",f"{type(e).__name__}: {e}")
        dados_score['pontuacao'] = 0
        motivos = ["Erro no cálculo de score"]

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos

# =========================
# FUNÇÕES DE EXIBIÇÃO.
# =========================
def mostrar_processos(lista, motivos):
    """
    Método mostrar_suspeitos, imprimi todas as informações relativas a processoas suspeitos.
    :param lista: Lista de processos.txt suspeitos (retorno da função anterior).
    :return: pid, nome, caminho e o utilizador do processo.
    """
    for item in lista:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("Identificação: \n")
        print(f"PID                  : {item['pid']}")
        print(f"PPID                 : {item['ppid']}")
        print(f"Nome                 : {item['nome']}")
        print(f"Utilizador           : {item['utilizador']}\n")
        print("Executável: \n")
        print(f"Caminho              : {item['caminho']}")
        print(f"Hash                 : {item['hash']}")
        print(f"Estado da assinatura : {item['assinatura']}\n")
        print("Avaliação: \n")
        print(f"Pontuação de risco   : {item['pontuacao']}")
        print(f"Nível de risco       : {item['risco']}")

    if (len(motivos) > 0):
        print("Motivos:", ", ".join(motivos))
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n")