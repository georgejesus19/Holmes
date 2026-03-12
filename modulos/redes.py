import os
import psutil
import socket
from modulos import logs
from uteis import validar_resposta

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

def verificar_conexoes_de_rede(mostrar=True):

    os.system("cls")
    print("Conexões de rede analisadas: \n")
    conexoes = list()
    temp = dict()

    for connection in psutil.net_connections(kind='inet'):
        pid = connection.pid

        # Nome do processo
        if pid is not None:
            try:
                proc = psutil.Process(pid)
                nome = proc.name()
                if not mostrar:
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

        temp['ip_local'] = connection.laddr.ip
        temp['porta_local'] = connection.laddr.port
        temp['endereco_remoto'] = ip_remoto
        temp['dominio'] = dominio
        temp['porta_remota'] = porta_remota
        temp['estado'] = connection.status
        temp['pid'] = pid
        temp['nome'] = nome

        logs.inserir_conexoes_rede(temp['ip_local'], temp['porta_local'],
                                   temp['endereco_remoto'], temp['dominio'],
                                   temp['porta_remota'], temp['estado'],
                                   temp['pid'], temp['nome'],
                                   "conexoes_rede")

        conexoes.append(temp.copy())
        if mostrar:
            mostrar_conexoes([temp.copy()])
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
                    'ip_local': ip['ip_local'],
                    'porta_local': ip['porta_local'],
                    'endereco_remoto': ip['endereco_remoto'],
                    'dominio': ip['dominio'],
                    'porta_remota': ip['porta_remota'],
                    'estado': ip['estado'],
                    'pid': ip['pid'],
                    'nome': ip['nome']
                })
                logs.inserir_conexoes_rede(ip['ip_local'], ip['porta_local'],
                                           ip['endereco_remoto'], ip['dominio'],
                                           ip['porta_remota'], ip['estado'],
                                           ip['pid'], ip['nome'], "conexoes_rede_suspeitas")
                pids.add(ip['pid'])
    os.system("cls")
    tamanho = len(suspeitos)
    if (tamanho > 0):
        print("Conxões suspeitas detetadas!")
        resposta = validar_resposta.validar_resposta()
        if (resposta in ["SIM", "S"]):
            logs.consultar_conexoes_rede("conexoes_rede_suspeitas")
    else:
        print("Não existem conexões de rede suspeitas\n")

def mostrar_conexoes(lista):
    for conexao in lista:
        print("------------------------------------------------------------")
        print(f"IP Local            : {conexao['ip_local']}")
        print(f"Porta Local         : {conexao['porta_local']}")
        print(f"Endereço Remoto     : {conexao['endereco_remoto']}")
        print(f"Dominio             : {conexao['dominio']}")
        print(f"Porta Remota        : {conexao['porta_remota']}")
        print(f"Estado da Conexão   : {conexao['estado']}")
        print(f"PID do Processo     : {conexao['pid']}")
        print(f"Nome do Processo    : {conexao['nome']}")
        print("------------------------------------------------------------")