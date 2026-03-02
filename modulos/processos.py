import os
import psutil
from modulos import logs
from uteis import verificar_assinatura_digital
from uteis import obter_hash
from uteis import variaveis_de_ambiente
from uteis import normalizar_caminho
from uteis import validar_resposta

def obter_processos(mostrar=True):
    """
    Método obter_processos, serve para obter todos os processoas.
    :return: Devolve uma lista de todos os processos.txt (programas em execução)
    """
    os.system("cls")
    print("Processos Analisados: \n")
    processos = list()  # recebe uma cópia dos valores dentro de temp.
    temp = dict()  # armazena valores como: 'pid', 'name', 'username', 'exe'
    assinatura = ""

    for process in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'exe']):
        if not mostrar:
            print(f"Processo em análise: {process.name()}")
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

        if (caminho in ['Acesso negado ou processo terminado', '', 'Registry']):
            temp['assinatura'] = 'Ignorado (Sistema)'

        if (os.path.exists(caminho) and caminho.lower().endswith('.exe')):
            temp['hash'] = obter_hash.obter_hash(caminho)
            assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
            if (assinatura == "Signature verified."):
                temp['assinatura'] = 'Válida'
            else:
                temp['assinatura'] = assinatura

        logs.inserir_processo(temp['pid'],temp['ppid'],
        temp['nome'], temp['caminho'],temp['utilizador'], temp['hash'],temp['assinatura'], "processos")

        processos.append(temp.copy())  # adiciona uma cópia do dicionário a lista de processos.
        if mostrar:
            mostrar_processos(processos)
    return processos


def obter_processos_suspeitos(ficheiro, lista_processos):
    """
    Método obter_processos_suspeitos, serve para marcar um processo como suspeito com base numa blacklist (ficheiro de texto).
    :param ficheiro: Corresponde ao ficheiro de texto usado como blacklist
    :param lista_processos: Corresponde a lista de todos os processos.txt (retorno da função anterior)
    :return: Uma lista com todos os processoas considerados suspeitos ou uma lista vazia (em caso de erro).
    """
    suspeitos = []  # armazena todos os processos.txt considerados suspeitos.
    pids_adicionados = set()  # conjunto de pids (serve para evitar duplicação).

    print("Processos Suspeitos: \n")

    for processo in lista_processos:
        if (processo['assinatura'] in ['Válida', 'Ignorado (Sistema)']):
            continue

        nome_processo = processo['nome'].lower().strip()
        caminho_processo = normalizar_caminho.normalizar(processo['caminho'])
        for valor_processo in ficheiro:
            if (valor_processo == nome_processo) or \
                (caminho_processo.startswith(variaveis_de_ambiente.expandir_caminhos(valor_processo))):
                if (processo['pid'] not in pids_adicionados):
                    # Adiciona todas as informações para a lista de suspeitos.
                    suspeitos.append({
                        'pid': processo['pid'],
                        'ppid': processo['ppid'],
                        'nome': processo['nome'],
                        'caminho': processo['caminho'],
                        'utilizador': processo['utilizador'],
                        'hash': processo['hash'],
                        'assinatura': processo['assinatura']
                    })
                    pids_adicionados.add(processo['pid'])

    os.system("cls")
    tamanho = len(suspeitos)
    if (tamanho > 0):
        print("Processos suspeitos detetados!")
        resposta = validar_resposta.validar_resposta()
        if (resposta in ["SIM", "S"]):
            logs.consultar_processos("processos_suspeitos")
    else:
        print("Não existem processos suspeitos\n")


def mostrar_processos(lista):
    """
    Método mostrar_suspeitos, imprimi todas as informações relativas a processoas suspeitos.
    :param lista: Lista de processos.txt suspeitos (retorno da função anterior).
    :return: pid, nome, caminho e o utilizador do processo.
    """
    tamanho = len(lista)
    if (tamanho > 0):
        for item in lista:
            print("------------------------------------------------------------")
            print(f"PID                    : {item['pid']}")
            print(f"PPID                   : {item['ppid']}")
            print(f"Nome                   : {item['nome']}")
            print(f"Caminho                : {item['caminho']}")
            print(f"Utilizador             : {item['utilizador']}")
            print(f"Hahs                   : {item['hash']}")
            print(f"Estado da assinatura   : {item['assinatura']}")
            print("------------------------------------------------------------")