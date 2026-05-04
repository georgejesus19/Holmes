import os
import psutil
import socket
from uteis import verificar_assinatura_digital
from uteis import obter_hash
from uteis import caminho_raiz
from uteis import pontos_assinatura
from uteis import carregar_lista

# =========================
# DECLARAÇÃO DE CONSTANTES.
# =========================
PORTAS_SUSPEITAS = {20, 21, 22, 23, 25, 53, 80, 110, 143,
                     445, 3306, 3389, 8080, 4444, 5555,
                    6666, 6667, 12345, 27374, 31337}

TLDs_SUSPEITAS = { ".tk", ".ml", ".ga", ".cf", ".gq",
                   ".top", ".xyz", ".monster", ".cyou",
                   ".club", ".click", ".support"}

# =========================
# FUNÇÕES AUXILIARES.
# =========================
def obter_dominio(endereco_ip):
    try:
        dominio = socket.gethostbyaddr(endereco_ip)[0]
    except (socket.herror, socket.gaierror) as erro:
        dominio = "Desconhecido"
    return dominio

def obter_caminho_binario(pid):
    try:
        binario = psutil.Process(pid)
        caminho = binario.exe()

        if not caminho:
            if pid == 4:
                return ''
            return "Desconhecido"
        return caminho
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return "Acesso negado ou processo terminado"

def verificar_tld(dominio, TLDs):
    dominio.lower().strip()
    for tld in TLDs:
        if (dominio.endswith(tld)):
            return True
    return False

def verificar_porta (porta, portas):
   return porta in portas

def verificar_dominio(dominio, lista_dominios):
    return dominio in lista_dominios

# =========================
# ANÁLISE PRINCIPAL.
# =========================
def verificar_conexoes_de_rede():

    os.system("cls")
    print("Conexões de rede analisadas: \n")
    conexoes = list()
    temp = dict()

    tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                        'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                        'UnknownError': 'Erro na verificação da assinatura digital'}

    lista_ips = carregar_lista.carregar_lista("listas/ips_suspeitos.txt")
    lista_dominios = carregar_lista.carregar_lista("listas/dominios_suspeitos.txt")

    for connection in psutil.net_connections(kind='inet'):
        pid = connection.pid
        caminho = obter_caminho_binario(pid)
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

        temp['ip_local'] = connection.laddr.ip
        temp['porta_local'] = connection.laddr.port
        temp['endereco_remoto'] = ip_remoto
        temp['dominio'] = dominio
        temp['porta_remota'] = porta_remota
        temp['estado'] = connection.status
        temp['pid'] = pid
        temp['nome'] = nome
        temp['caminho'] = caminho
        temp['assinatura'] = ''
        temp['status'] = ''
        temp['hash'] = ''
        temp['pontuacao'] = 0
        temp['risco'] = ''


        if (caminho.strip() in ['Acesso negado ou processo terminado', '', 'Registry']):
            temp['assinatura'] = 'Ignorado (Sistema)'
            temp['hash'] = 'Ignorado (Sistema)'
            temp['status'] = 'Valid'
        if (os.path.exists(caminho) and caminho.lower().endswith('.exe')):
            assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
            temp['hash'] = obter_hash.obter_hash(caminho)
            temp['status'] = assinatura
            temp['assinatura'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")

        else:
            if (pid != 0 and pid != 4):
                temp['assinatura'] = 'Erro ao obter assinatura digital (caminho inválido ou inexistente)'
                temp['hash'] = 'Erro ao obter hash (caminho inválido ou inexistente)'
                temp['status'] = 'Valid'

        item = verificar_conexoes_suspeitas(temp.copy(), lista_ips, lista_dominios)
        temp['pontuacao'] = item[0]['pontuacao']
        temp['risco'] = item[0]['risco']
        conexoes_copia = temp.copy()
        conexoes.append(conexoes_copia)
        mostrar_conexoes([conexoes_copia], item[1])


def verificar_conexoes_suspeitas(conexao, lista_ips, lista_dominios):

    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    endereco_remoto = conexao['endereco_remoto'].lower()
    dominio = conexao['dominio'].strip()
    porta = conexao['porta_remota']
    caminho_conexao = conexao['caminho']

    score, motivo = pontos_assinatura.pontos_assinatura(conexao['status'])
    dados_score['pontuacao'] += score
    if (conexao['status'] != "Valid"):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_conexao)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    if (endereco_remoto in lista_ips):
        dados_score['pontuacao'] += 50
        motivos.append("IP presente em blacklist")

    if (verificar_tld(dominio, TLDs_SUSPEITAS)):
        dados_score['pontuacao'] += 25
        motivos.append("TLD suspeito")

    if (verificar_dominio(dominio, lista_dominios)):
        dados_score['pontuacao'] += 40
        motivos.append("Domínio suspeito")

    if (verificar_porta(porta, PORTAS_SUSPEITAS)):
        dados_score['pontuacao'] += 20
        motivos.append("Porta incomum")

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))

    if (dados_score['pontuacao'] >= 0 and dados_score['pontuacao'] <= 30):
        dados_score['risco'] = 'Baixo'
    elif (dados_score['pontuacao'] > 30 and dados_score['pontuacao'] <= 60):
        dados_score['risco'] = 'Médio'
    else:
        dados_score['risco'] = 'Alto'

    return dados_score, motivos

# =========================
# FUNÇÕES DE EXIBIÇÃO.
# =========================
def mostrar_conexoes(lista, motivos):
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
        print(f"Caminho processo    : {conexao['caminho']}")
        print(f"Assinatura digital  : {conexao['assinatura']}")
        print(f"Hash do executável  : {conexao['hash']}")
        print(f"Pontuação de risco  : {conexao['pontuacao']}")
        print(f"Nível de risco      : {conexao['risco']}")
        print("------------------------------------------------------------")
    if (len(motivos) > 0):
        print("Motivos: ")
        for motivo in motivos:
            print(f" - {motivo}")
    print("\n")