import os
import psutil
import socket

PORTAS_SUSPEITAS = {20, 21, 22, 23, 25, 53, 80, 110, 143,
                    443, 445, 3306, 3389, 8080, 4444, 5555,
                    6666, 6667, 12345, 27374, 31337}

TLDs_SUSPEITAS = { ".tk", ".ml", ".ga", ".cf", ".gq",
                   ".top", ".xyz", ".monster", ".cyou",
                   ".club", ".click", ".support"}

def obter_dominio(endereco_ip):
    try:
        dominio = socket.gethostbyaddr(endereco_ip)[0]
    except Exception as error:
        dominio = 'Houve uma excessão ao tentar obter o domínio'
    return dominio

def verificar_tld(dominio, TLDs):
    for tld in TLDs:
        if (dominio.lower().strip().endswith(tld)):
            return True
    return False

def verificar_dominio(dominio):
    dominios = []
    try:
        with open("../listas/dominios_suspeitos.txt", "r") as dominios_suspeitos:
            for linha in dominios_suspeitos:
                dominios.append(linha.lower().strip())
        return dominio.lower().strip() in dominios
    except (FileNotFoundError, IOError, NameError) as erro:
        print(f'Erro na abertura do ficheiro: {erro}')
        return False

def verificar_conexoes_de_rede():

    conexoes = list()
    temp = dict()

    for connection in psutil.net_connections(kind='inet'):
        pid = connection.pid

        # Nome do processo
        if pid is not None:
            try:
                proc = psutil.Process(pid)
                nome = proc.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                nome = "Desconhecido"
        else:
            nome = "Sem PID"

        # Obtém o endereço remoto e a porta remota
        if connection.raddr:
            ip_remoto = connection.raddr[0]
            porta_remota = connection.raddr[1]
            dominio = obter_dominio(ip_remoto)
        else:
            ip_remoto = "Sem conexão remota"
            porta_remota = "Sem porta remota"
            dominio = "Sem domínio"

        temp['endereco_local'] = connection.laddr
        temp['endereco_remoto'] = ip_remoto
        temp['dominio'] = dominio
        temp['porta_remota'] = porta_remota
        temp['estado'] = connection.status
        temp['pid'] = pid
        temp['nome'] = nome

        conexoes.append(temp.copy())
    return conexoes

def verificar_conexoes_suspeitas(conexoes, ficheiro):
    suspeitos = []
    pids = set()
    try:
        with open(ficheiro, 'r') as lista_ips:
            for linha in lista_ips:
                valor_ip = linha.strip().lower()
                for ip in conexoes:

                    endereco_remoto = ip['endereco_remoto'].lower()
                    dominio = ip['dominio'].strip()

                    if (endereco_remoto == valor_ip) or \
                       (verificar_tld(dominio, TLDs_SUSPEITAS)) or \
                       (verificar_dominio(dominio)):

                        if (ip['pid'] not in pids):
                            suspeitos.append({
                                'endereco_local' : ip['endereco_local'],
                                'endereco_remoto' : ip['endereco_remoto'],
                                'dominio' : ip['dominio'],
                                'porta_remota' : ip['porta_remota'],
                                'estado' : ip['estado'],
                                'pid' : ip['pid'],
                                'nome' : ip['nome']
                            })
                            pids.add(ip['pid'])
        return suspeitos
    except (FileNotFoundError, IOError, NameError) as erro:
        print(f'Erro na abertura do ficheiro: {erro}')
        return [] 

def mostrar_conexoes(lista, mensagem="Conexões de Rede ativas:\n"):
    tamanho = len(lista)
    if (tamanho > 0):
        print(mensagem)
        print("------------------------------------------------------------")
        for conexao in lista:
            print(f"Endereço Local      : {conexao['endereco_local']}")
            print(f"Endereço Remoto     : {conexao['endereco_remoto']}")
            print(f"Dominio             : {conexao['dominio']}")
            print(f"Porta Remota        : {conexao['porta_remota']}")
            print(f"Estado da Conexão   : {conexao['estado']}")
            print(f"PID do Processo     : {conexao['pid']}")
            print(f"Nome do Processo    : {conexao['nome']}")
            print("------------------------------------------------------------")
    else:
        print("Não existem conexões suspeitas")

    input("Pressione enter para continuar...")
    os.system("cls")

conexoes = verificar_conexoes_de_rede()
#mostrar_conexoes(verificar_conexoes_suspeitas(conexoes, "../listas/ips_suspeitos.txt"),
                 #"Conexões suspeitas:\n")
mostrar_conexoes(conexoes)


