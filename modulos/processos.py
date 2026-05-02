import os
import psutil
from uteis import verificar_assinatura_digital
from uteis import obter_hash
from uteis import variaveis_de_ambiente
from uteis import normalizar_caminho
from uteis import caminho_raiz
from uteis import carregar_lista


def pontos_assinatura(estado_assinatura):
    if (estado_assinatura == 'NotSigned'):
        return 20, "Sem assinatura digital"
    elif (estado_assinatura == 'HashMismatch'):
        return 40, "Ficheiro alterado"
    elif (estado_assinatura == 'NotTrusted'):
        return 35, "Certificado não confiável"
    elif (estado_assinatura == 'UnknownError'):
        return 15, "Erro ao verificar assinatura digital"
    return -10, "Assinatura digital válida"


def obter_processos():
    """
    Método obter_processos, serve para obter todos os processoas.
    :return: Devolve uma lista de todos os processos.txt (programas em execução)
    """
    os.system("cls")
    print("Processos Analisados: \n")

    processos = list()  # recebe uma cópia dos valores dentro de temp.
    temp = dict()  # armazena valores como: 'pid', 'name', 'username', 'exe'
    assinatura = ""
    tipos_assinatura = {'Valid':'Válida', 'NotSigned':'Sem assinatura',
                        'HashMismatch':'Ficheiro alterado', 'NotTrusted':'Certificado inválido',
                        'UnknownError':'Erro na verificação da assinatura digital'}

    lista = carregar_lista.carregar_lista("listas/blacklist.txt")

    for process in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'exe']):
        # Tenta atribuir o caminho do executável.
        try:
            caminho = process.exe()
        # Em caso de exceções atribui uma string a variavel.
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            caminho = "Acesso negado ou processo terminado"
        # Atribui o valor a  cada chave do dicionário
        temp['pid'] = process.pid  # pid (process id)
        temp['ppid'] = process.ppid()  # ppid (parent process id)
        temp['nome'] = process.name()
        temp['caminho'] = caminho
        temp['utilizador'] = process.username()
        temp['hash'] = ''
        temp['assinatura'] = ''
        temp['status'] = ''
        temp['pontuacao'] = 0
        temp['risco'] = ''

        if (caminho in ['Acesso negado ou processo terminado', '', 'Registry']):
            temp['assinatura'] = 'Ignorado (Sistema)'
            temp['hash'] = 'Ignorado (Sistema)'

        if (os.path.exists(caminho) and caminho.lower().endswith('.exe')):
            temp['hash'] = obter_hash.obter_hash(caminho)
            assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)

            temp['status'] = assinatura
            temp['assinatura'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")
        item = obter_processos_suspeitos(lista, temp.copy())
        temp['pontuacao'] = item[0]['pontuacao']
        temp['risco'] = item[0]['risco']
        processos_copia = temp.copy()
        processos.append(processos_copia)  # adiciona uma cópia do dicionário a lista de processos.
        if (temp['pontuacao'] > 0):
            mostrar_processos([processos_copia], item[1])



def obter_processos_suspeitos(ficheiro, processo):
    """
    Método obter_processos_suspeitos, serve para marcar um processo como suspeito com base numa blacklist (ficheiro de texto).
    :param ficheiro: Corresponde ao ficheiro de texto usado como blacklist
    :param lista_processos: Corresponde a lista de todos os processos.txt (retorno da função anterior)
    :return: Uma lista com todos os processoas considerados suspeitos ou uma lista vazia (em caso de erro).
    """
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []


    score_local = 0
    motivos_locais = []

    nome_achado = False
    caminho_achado = False
    nome_presente = False
    caminho_presente = False

    nome_processo = processo['nome'].lower().strip()
    caminho_processo = normalizar_caminho.normalizar(processo['caminho'])

    score, motivo = pontos_assinatura(processo['status'])
    dados_score['pontuacao'] += score
    if (processo['status'] != "Valid"):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_processo)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    for valor_processo in ficheiro:
        valor_processo = valor_processo.lower().strip()

        if not nome_achado:
            if (valor_processo == nome_processo):
                nome_presente = True
                nome_achado = True

        if not caminho_achado:
            if (caminho_processo.startswith(variaveis_de_ambiente.expandir_caminhos(valor_processo))):
                caminho_presente = True
                caminho_achado = True

        if (nome_presente and caminho_presente):
            score_local = 60
            motivos_locais = ["Nome e caminho presentes na blacklist"]
            break

        elif (nome_presente):
            score_local = 40
            motivos_locais = ["Nome presente na blacklist"]

        elif (caminho_presente):
            score_local = 40
            motivos_locais = ["Caminho presente na blacklist"]

    dados_score['pontuacao'] += score_local
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))

    if (dados_score['pontuacao'] >= 0 and dados_score['pontuacao'] <= 30):
        dados_score['risco'] = 'Baixo'
    elif (dados_score['pontuacao'] > 30 and dados_score['pontuacao'] <= 60):
        dados_score['risco'] = 'Médio'
    else:
        dados_score['risco'] = 'Alto'

    return dados_score, motivos

def mostrar_processos(lista, motivos):
    """
    Método mostrar_suspeitos, imprimi todas as informações relativas a processoas suspeitos.
    :param lista: Lista de processos.txt suspeitos (retorno da função anterior).
    :return: pid, nome, caminho e o utilizador do processo.
    """
    for item in lista:
        print("------------------------------------------------------------")
        print(f"PID                    : {item['pid']}")
        print(f"PPID                   : {item['ppid']}")
        print(f"Nome                   : {item['nome']}")
        print(f"Caminho                : {item['caminho']}")
        print(f"Utilizador             : {item['utilizador']}")
        print(f"Hahs                   : {item['hash']}")
        print(f"Estado da assinatura   : {item['assinatura']}")
        print(f"Pontuação de risco     : {item['pontuacao']}")
        print(f"Nível de risco         : {item['risco']}")
        print("------------------------------------------------------------")
    if (len(motivos) > 0):
        print("Motivos: ")
        for motivo in motivos:
            print(f" - {motivo}")
    print("\n")
