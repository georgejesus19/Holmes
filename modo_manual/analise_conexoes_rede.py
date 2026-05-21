import os
import psutil
from modulos import redes as r
from modulos import logs as l
from uteis import atribuir_risco
from uteis import pontos_assinatura
from uteis import caminho_raiz
from uteis import carregar_lista
from uteis import criar_string
from uteis import selecionar_valor

# =========================
# FUNÇÕES AUXILIARES.
# =========================

def ip_local(ip):
    return (
        ip.startswith("127.") or
        ip.startswith("192.168.") or
        ip.startswith("10.") or
        ip.startswith("172.") or
        ip == "::1"
    )

def analisar_conexao_rede(tipos_assinatura):

    os.system("cls")
    conexoes = list()
    temporario = dict()
    cache_processos = dict()
    cache_dns = dict()
    dominio = ''
    ppid = 0

    lista_ips = carregar_lista.carregar_lista("listas/ips_suspeitos.txt")
    lista_dominios = carregar_lista.carregar_lista("listas/dominios_suspeitos.txt")

    print("Conexões de rede disponíveis para análise: \n")

    for connection in psutil.net_connections(kind='inet'):
        pid = connection.pid
        # Nome do processo
        if pid is None:
            nome = "Sem PID"
            caminho = ""
        else:
            if pid in cache_processos:
                nome, caminho = cache_processos[pid]
            else:
                try:
                    proc = psutil.Process(pid)
                    nome = proc.name()
                    ppid = proc.ppid()
                    caminho = r.obter_caminho_binario(pid)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    nome = "Desconhecido"
                    caminho = "Acesso negado ou processo terminado"
                cache_processos[pid] = (nome, caminho)

        # Obtém o endereço remoto e a porta remota
        if connection.raddr:
            ip_remoto = connection.raddr[0]
            porta_remota = connection.raddr[1]
        else:
            ip_remoto = "Sem conexão remota"
            porta_remota = "Sem porta remota"
            dominio = "Sem domínio"

        temporario['ip_local'] = connection.laddr.ip
        temporario['porta_local'] = connection.laddr.port
        temporario['endereco_remoto'] = ip_remoto
        temporario['dominio'] = dominio
        temporario['porta_remota'] = porta_remota
        temporario['estado'] = connection.status
        temporario['pid'] = pid
        temporario['ppid'] = ppid
        temporario['nome'] = nome
        temporario['caminho'] = caminho

        conexoes.append(temporario.copy())

    item = selecionar_valor.selecionar_valor(conexoes)

    os.system("cls")

    if ip_local(item['endereco_remoto']):
        item['dominio'] = "Local"
    else:
        if item['endereco_remoto'] in cache_dns:
            item['dominio'] = cache_dns[item['endereco_remoto']]
        else:
            item['dominio'] = r.obter_dominio(item['endereco_remoto'])
            cache_dns[item['endereco_remoto']] = item['dominio']

    resultado_consulta = r.verificar_caminho_conexao_rede(item['caminho'], tipos_assinatura, item['pid'], item['ppid'], item['nome'])

    caminho = resultado_consulta['caminho']
    status = resultado_consulta['status']
    assinatura = resultado_consulta['assinatura_digital']
    hash = resultado_consulta['hash']

    info_score = calcular_score_conexoes_rede(item, lista_ips, lista_dominios, status, caminho)

    pontuacao = info_score[0]['pontuacao']
    risco = info_score[0]['risco']
    motivos = criar_string.criar_string_motivo(info_score[1])

    print("Dados da conexão de rede: ")
    print("----------------------------------------------")
    print(f"IP Local            : {item['ip_local']}")
    print(f"Porta Local         : {item['porta_local']}")
    print(f"Endereço Remoto     : {item['endereco_remoto']}")
    print(f"Dominio             : {item['dominio']}")
    print(f"Porta Remota        : {item['porta_remota']}")
    print(f"Estado da Conexão   : {item['estado']}")
    print(f"PID do Processo     : {item['pid']}")
    print(f"Nome do Processo    : {item['nome']}")
    print(f"Caminho processo    : {caminho}")
    print(f"Assinatura digital  : {assinatura}")
    print(f"Hash do executável  : {hash}")
    print(f"Pontuação de risco  : {pontuacao}")
    print(f"Nível de risco      : {risco}")
    print(f"Motivos             : {motivos}")
    print("----------------------------------------------")

    id_processo = l.consultar_processo(item['pid'])
    l.inserir_conexoes_rede(item['ip_local'], item['porta_local'], item['endereco_remoto'],
                               item['dominio'], item['porta_remota'], item['estado'], pontuacao,
                               risco, motivos, id_processo["id"])

def calcular_score_conexoes_rede(conexao, lista_ips, lista_dominios, status, caminho):

    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    endereco_remoto = conexao['endereco_remoto'].lower()
    dominio = conexao['dominio'].strip()
    porta = conexao['porta_remota']
    caminho_conexao = caminho

    score, motivo = pontos_assinatura.pontos_assinatura(status)
    dados_score['pontuacao'] += score
    if (status not in ["Valid", "Sistema"]):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_conexao)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    if (endereco_remoto in lista_ips):
        dados_score['pontuacao'] += 50
        motivos.append("IP presente em blacklist")

    if (r.verificar_tld(dominio, r.TLDs_SUSPEITAS)):
        dados_score['pontuacao'] += 25
        motivos.append("TLD suspeito")

    if (r.verificar_dominio(dominio, lista_dominios)):
        dados_score['pontuacao'] += 40
        motivos.append("Domínio suspeito")

    if (r.verificar_porta(porta, r.PORTAS_SUSPEITAS)):
        dados_score['pontuacao'] += 20
        motivos.append("Porta incomum")

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos
