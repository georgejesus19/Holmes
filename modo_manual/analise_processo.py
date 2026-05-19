import os
import psutil
from uteis import normalizar_caminho
from uteis import obter_hash
from uteis import calcular_score
from uteis import atribuir_risco
from uteis import pontos_assinatura
from uteis import verificar_assinatura_digital
from uteis import caminho_raiz
from uteis import validar_resposta
from uteis import carregar_lista
from uteis import criar_string
from acoes import processo


# =========================
# ANÁLISE PRINCIPAL & CÁLCULO DE SCORE
# =========================

def analisar_processo(tipos_assinatura):
    os.system("cls")
    temporario = dict() # Irá armazenar de forma temporário dados relativos a um processo.
    processos = list() # Irá armazenar os respectivos dados vindos do dicionário temporário.

    ficheiro = carregar_lista.carregar_lista("listas/blacklist.txt")

    print("Processos disponíveis para análise: \n")

    for process in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'exe']):
        try:
            caminho = process.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            caminho = "Acesso negado ou processo terminado"
        temporario['pid'] = process.pid
        temporario['ppid'] = process.ppid()
        temporario['nome'] = process.name()
        temporario['caminho'] = normalizar_caminho.normalizar(caminho)
        temporario['utilizador'] = process.username()
        temporario['status'] = ''
        temporario['pontuacao'] = 0
        temporario['risco'] = ''

        if (temporario['nome'].endswith(".exe")):
            processos.append(temporario.copy())


    item = selecionar_valor(processos)

    os.system("cls")

    status = verificar_assinatura_digital.verificar_assinatura(item['caminho'])
    assinatura = tipos_assinatura.get(status, "Assinatura digital desconhecida")
    hash_processo = obter_hash.obter_hash(item['caminho'])

    info_score = calcular_score_processo(ficheiro, item, status)

    pontuacao = info_score[0]['pontuacao']
    risco = info_score[0]['risco']
    motivos = criar_string.criar_string_motivo(info_score[1])

    print("Dados do binário:")
    print("--------------------")
    print(f"PID: {item['pid']}")
    print(f"PPID: {item['ppid']}")
    print(f"Nome: {item['nome']}")
    print(f"Caminho: {item['caminho']}")
    print(f"Utilizador do processo: {item['utilizador']}")
    print(f"Hash do executável: {hash_processo}")
    print(f"Estado da assinatura digital: {assinatura}")
    print(f"Pontuação de risco: {pontuacao}")
    print(f"Nível de risco: {risco}")
    print(f"Motivos: {motivos}")
    print("--------------------")

    resposta = validar_resposta.validar_resposta("Deseja terminar o processo")

    if (resposta in ["SIM", "S"]):
        processo.terminar_processo(item['pid'])

def calcular_score_processo(ficheiro, processo, status):
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    caminho_processo = normalizar_caminho.normalizar(processo['caminho'])

    score, motivo = pontos_assinatura.pontos_assinatura(status)
    dados_score['pontuacao'] += score

    if (status not in ["Valid", "Sistema"]):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_processo)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    score_local, motivos_locais = calcular_score.calcular_score_auxiliar(ficheiro, processo['nome'], caminho_processo)

    dados_score['pontuacao'] += score_local['pontuacao']
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos
