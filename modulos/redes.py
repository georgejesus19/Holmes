import os
import psutil
import socket

PORTAS_SUSPEITAS = {20, 21, 22, 23, 25, 53, 80, 110, 143,
                     445, 3306, 3389, 8080, 4444, 5555,
                    6666, 6667, 12345, 27374, 31337}

TLDs_SUSPEITAS = { ".tk", ".ml", ".ga", ".cf", ".gq",
                   ".top", ".xyz", ".monster", ".cyou",
                   ".club", ".click", ".support"}

def obter_dominio(endereco_ip):
    try:
        dominio = socket.gethostbyaddr(endereco_ip)[0]
    except (socket.herror, socket.gaierror) as erro:
        dominio = "Desconhecido"
    return dominio

def verificar_tld(dominio, TLDs):
    for tld in TLDs:
        if (dominio.lower().strip().endswith(tld)):
            return True
    return False

def verificar_porta (porta, portas):
   return porta in portas

def verificar_dominio(dominio, lista_dominios):
    return dominio in lista_dominios

def verificar_conexoes_de_rede():

    os.system("cls")
    conexoes = list()
    temp = dict()

    for connection in psutil.net_connections(kind='inet'):
        pid = connection.pid

        # Nome do processo
        if pid is not None:
            try:
                proc = psutil.Process(pid)
                nome = proc.name()
                print(f"Conexão em análise: {nome}")
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

def verificar_conexoes_suspeitas(conexoes, lista_ips, lista_dominios):

    os.system("cls")

    suspeitos = []
    pids = set()

    for ip in conexoes:
        endereco_remoto = ip['endereco_remoto'].lower()
        dominio = ip['dominio'].strip()
        porta = ip['porta_remota']

        # verifica se é suspeito
        if  (endereco_remoto in lista_ips) or \
            (verificar_tld(dominio, TLDs_SUSPEITAS)) or \
            (verificar_dominio(dominio, lista_dominios)) or \
            (verificar_porta(porta, PORTAS_SUSPEITAS)):

            if ip['pid'] not in pids:
                suspeitos.append({
                    'endereco_local': ip['endereco_local'],
                    'endereco_remoto': ip['endereco_remoto'],
                    'dominio': ip['dominio'],
                    'porta_remota': ip['porta_remota'],
                    'estado': ip['estado'],
                    'pid': ip['pid'],
                    'nome': ip['nome']
                })
                pids.add(ip['pid'])
    return suspeitos

def mostrar_conexoes(lista, mensagem="Conexões de Rede ativas:\n"):
    os.system("cls")
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

#conexoes = verificar_conexoes_de_rede()
#mostrar_conexoes(verificar_conexoes_suspeitas(conexoes, "../listas/ips_suspeitos.txt"),
                 #"Conexões suspeitas:\n")
#mostrar_conexoes(conexoes)


