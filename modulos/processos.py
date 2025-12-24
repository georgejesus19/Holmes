import psutil
import hashlib
import os
from uteis import verificar_assinatura_digital

def obter_hash(caminho, tipo_hash="sha256"):
    hash_func = hashlib.new(tipo_hash)
    try:
        with open(caminho, "rb") as ficheiro:
            for p in iter(lambda: ficheiro.read(4096), b""):
                hash_func.update(p)
        return hash_func.hexdigest()
    except (FileNotFoundError, IOError, NameError) as erro:
        print(f"Erro durante a obtenção do hash: {erro}")
        return ""

def obter_processos():
    """
    Método obter_processos, serve para obter todos os processoas.
    :return: Devolve uma lista de todos os processos.txt (programas em execução)
    """
    os.system("cls")
    processos = list() # recebe uma cópia dos valores dentro de temp.
    temp = dict() # armazena valores como: 'pid', 'name', 'username', 'exe'
    assinatura = ""

    for process in psutil.process_iter(['pid','ppid', 'name', 'username', 'exe']):
        print(f"Processo em análise: {process.name()}")
        # Tenta atribuir o caminho do executável.
        try:
            caminho = process.exe()
        # Em caso de exceções atribui uma string a variavel.
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            caminho = "Acesso negado ou processo terminado"
        # Atribui o valor a  cada chave do dicionário
        temp['pid'] = process.pid # pid (process id)
        temp['ppid'] = process.ppid() #ppid (parent process id)
        temp['nome'] = process.name()
        temp['caminho'] = caminho
        temp['utilizador'] = process.username()
        temp['hash'] = ''
        temp['assinatura'] = ''

        if (caminho in ['Acesso negado ou processo terminado', '', 'Registry']):
            temp['assinatura'] = 'Ignorado (Sistema)'

        if (os.path.exists(caminho) and caminho.lower().endswith('.exe')):
            temp['hash'] = obter_hash(caminho)
            assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
            if (assinatura == "Signature verified."):
                temp['assinatura'] = 'Válida'
            else:
                temp['assinatura'] = assinatura

        processos.append(temp.copy()) # adiciona uma cópia do dicionário a lista de processos.
    return processos

def obter_processos_suspeitos(ficheiro, lista_processos):
    """
    Método obter_processos_suspeitos, serve para marcar um processo como suspeito com base numa blacklist (ficheiro de texto).
    :param ficheiro: Corresponde ao ficheiro de texto usado como blacklist
    :param lista_processos: Corresponde a lista de todos os processos.txt (retorno da função anterior)
    :return: Uma lista com todos os processoas considerados suspeitos ou uma lista vazia (em caso de erro).
    """
    suspeitos = [] # armazena todos os processos.txt considerados suspeitos.
    pids_adicionados = set() # conjunto de pids (serve para evitar duplicação).

    try:
        with open(ficheiro, 'r') as blacklist:
            for linha in blacklist:
                valor_processo = linha.strip().lower() # remove os espaços e transforma a string em minúscual
                # antes de atribuir a variável.

                for processo in lista_processos:
                    if (processo['assinatura'] in ['Válida', 'Ignorado (Sistema)']):
                        continue

                    nome_processo = processo['nome'].lower().strip()
                    caminho_processo = processo['caminho'].lower().strip()

                    if (valor_processo == nome_processo) or \
                       (caminho_processo.startswith(valor_processo)):
                        if (processo['pid'] not in pids_adicionados):
                            # Adiciona todas as informações para a lista de suspeitos.
                            suspeitos.append({
                                'pid': processo['pid'],
                                'ppid':processo['ppid'],
                                'nome': processo['nome'],
                                'caminho': processo['caminho'],
                                'utilizador': processo['utilizador'],
                                'hash' : processo['hash'],
                                'assinatura' : processo['assinatura']
                            })
                            pids_adicionados.add(processo['pid'])
        return suspeitos

    except (FileNotFoundError, IOError, NameError) as erro:
        print(f'Erro na abertura do ficheiro: {erro}')
        return []

def mostrar_processos(lista):
    """
    Método mostrar_suspeitos, imprimi todas as informações relativas a processoas suspeitos.
    :param lista: Lista de processos.txt suspeitos (retorno da função anterior).
    :return: pid, nome, caminho e o utilizador do processo.
    """
    os.system("cls")
    tamanho = len(lista)
    if (tamanho > 0):
        for item in lista:
            print(f"PID: {item['pid']}\nPPID: {item['ppid']}\nNome: {item['nome']}\nCaminho: {item['caminho']}\nUtilizador: {item['utilizador']}\nHash: {item['hash']}\nEstado da assinatura: {item['assinatura']}")
            print("-=" * 25)
    else:
        print("Não existem processos suspeitos.")

    input("Pressione Enter para continuar...")
    os.system("cls")

#processos = obter_processos()
#suspeitos = obter_processos_suspeitos("../listas/blacklist.txt", processos)
#mostrar_processos(processos)




