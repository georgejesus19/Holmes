import os
import psutil
from CLI import painel
from CLI import cores
from modulos import processos as p
from modulos import logs as l
from modulos import interface
from uteis import normalizar_caminho
from uteis import calcular_score
from uteis import atribuir_risco
from uteis import pontos_assinatura
#from uteis import caminho_raiz
from uteis import validar_resposta
from uteis import carregar_lista
from uteis import criar_string
from uteis import selecionar_valor
from acoes import processo
from datetime import datetime

# =========================
# ANÁLISE PRINCIPAL & CÁLCULO DE SCORE
# =========================

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def analisar_processo(tipos_assinatura):
    """
    :param tipos_assinatura: ficheiro com tradução diretado significaodo dos tipos de assinatura
    """
    os.system("cls")
    temporario = dict() # Irá armazenar de forma temporário dados relativos a um processo.
    processos = list() # Irá armazenar os respectivos dados vindos do dicionário temporário.

    ficheiro = carregar_lista.carregar_lista("listas/blacklist.txt")
    frase = "Processos disponíveis para análise:"
    print()

    print(interface.linhas(len(frase) + 10, "_"), "\n")
    print(f"{frase} \n")
    print(interface.linhas(len(frase) + 10, "_"))
    print("\n")

    for process in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'exe']):
        try:
            temporario['pid'] = process.pid
            temporario['ppid'] = process.ppid()
            temporario['nome'] = process.name()
            temporario['utilizador'] = process.username()

            if (temporario['nome'].endswith(".exe")):
                processos.append(temporario.copy())

        except Exception as e:
            print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a análise de um processo (verificar logs de erro){cores.CORES['limpo']}")
            erro = f"{type(e).__name__}: {e}"
            l.inserir_log_erro("erro", "processos", data_atual, erro)
            continue

    item = selecionar_valor.selecionar_valor(processos, len(frase))

    if item == 0:
        return

    os.system("cls")

    try:
        P = psutil.Process(item['pid'])
        caminho = P.exe()
    except (psutil.AccessDenied, psutil.NoSuchProcess):
        caminho = "Acesso negado ou processo terminado"

    try:
        resultado_consulta = p.verificar_dados_caminho(caminho, tipos_assinatura)

        caminho = resultado_consulta['caminho']
        status = resultado_consulta['status']
        assinatura = resultado_consulta['assinatura_digital']
        hash_processo = resultado_consulta['hash']

        info_score = calcular_score_processo(ficheiro, item, status, caminho)

        pontuacao = info_score[0]['pontuacao']
        risco = info_score[0]['risco']
        motivos = criar_string.criar_string_motivo(info_score[1])
        painel.painel_de_processo(item['pid'], item['ppid'], item['nome'], caminho, item['utilizador'],
                                  hash_processo, assinatura, pontuacao, risco, motivos)

        if (l.consultar_processo(item['pid'])):
            l.update_processo(item['pid'], item['utilizador'], pontuacao, risco, motivos)
        else:
            id_binario = l.consultar_binario(caminho)
            l.inserir_processo(item['pid'], item['ppid'], item['nome'], item['utilizador'], pontuacao,
                               risco, motivos, id_binario["id"])

        resposta = validar_resposta.validar_resposta("Deseja terminar o processo")

        if (resposta in ["SIM", "S"]):
            processo.terminar_processo(item['pid'], caminho)

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a consulta da tabela binários (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        l.inserir_log_erro("erro", "processos", data_atual, erro)


def calcular_score_processo(ficheiro, processo, status, caminho):
    """
    :param ficheiro: Lista de referência (blacklist)
    :param processo: processo analisado
    :param status: estado da assinatura digital
    :param caminho: caminho do processo analisado
    """
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    try:
        caminho_processo = normalizar_caminho.normalizar(caminho)

        score, motivo = pontos_assinatura.pontos_assinatura(status)
        dados_score['pontuacao'] += score

        if (status not in ["Valid", "Sistema"]):
            motivos.append(motivo)

        score_local, motivos_locais = calcular_score.calcular_score_auxiliar(ficheiro, processo['nome'],
                                                                             caminho_processo)
        dados_score['pontuacao'] += score_local['pontuacao']
        motivos.extend(motivos_locais)

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante o cálculo de score (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        l.inserir_log_erro("erro","processos", data_atual, erro)

        dados_score['pontuacao'] = 0
        motivos = ["Erro no cálculo de score"]

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos