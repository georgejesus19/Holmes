import os
import psutil
import socket
from CLI import cores
from modulos import logs
from uteis import verificar_assinatura_digital
from uteis import obter_hash
from uteis import caminho_raiz
from uteis import pontos_assinatura
from uteis import carregar_lista
from uteis import criar_string
from uteis import atribuir_risco
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# =========================
# DECLARAÇÃO DE CONSTANTES.
# =========================
PORTAS_SUSPEITAS = {666, 801, 999, 1005, 1015,
                    1025, 1030, 1042, 1075, 1080,
                    1170, 1234, 1243, 1337, 4444,
                    5555, 6666,6667,12345,27374,
                    31337}

TLDs_SUSPEITAS = {".tk", ".ml", ".ga",".cf",
                  ".gq", ".top", ".xyz", ".monster",
                  ".cyou", ".click", ".icu", ".faith", ".bid",
                  ".cd", ".jetzt"}

# =========================
# FUNÇÕES AUXILIARES.
# =========================
def obter_dominio(endereco_ip):
    """
    :param endereco_ip: endereço ip remoto
    :return: devolve o domínio associado ao endereço remoto
    """
    try:
        dominio = socket.gethostbyaddr(endereco_ip)[0]
    except (socket.herror, socket.gaierror) as erro:
        dominio = "Desconhecido"
    return dominio

def obter_caminho_binario(pid):
    """
    :param pid: pid do processo associado a conexão de rede
    :return: caminho do processo
    """
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
    """
    :param dominio: recebe o domínio associado a TLD
    :param TLDs: lista de TLDs
    :return: devolve true caso ele tenha a tld e false caso não tenha
    """
    dominio.lower().strip()
    for tld in TLDs:
        if (dominio.endswith(tld)):
            return True
    return False

def verificar_porta (porta, portas):
   return porta in portas

def verificar_dominio(dominio, lista_dominios):
    return dominio in lista_dominios

def verificar_caminho_conexao_rede(caminho, tipos_assinatura, pid, ppid, nome):
    """
    :param caminho: caminho do processo associado a conexão
    :param tipos_assinatura: ficheiro com tradução diretado significaodo dos tipos de assinatura
    :param pid: pid do processo
    :param ppid: ppid do processo
    :param nome: nome do processo associado a conexão
    :return: dicionário preenchido com dados
    """
    dados = {'id_binario': 0,'caminho': caminho,'hash': '','assinatura_digital': '','status': ''}

    try:
        resultado = logs.consultar_binario(caminho)

        if resultado:
            dados.update(resultado)
            dados['id_binario'] = resultado["id"]

        else:

            if caminho.strip() in ['Acesso negado ou processo terminado', '', 'Registry']:
                dados['assinatura_digital'] = 'Ignorado (Sistema)'
                dados['hash'] = 'Ignorado (Sistema)'
                dados['status'] = 'Sistema'

            else:
                assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
                dados['hash'] = obter_hash.obter_hash(caminho)
                dados['status'] = assinatura
                dados['assinatura_digital'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")

            logs.inserir_binario(dados['caminho'], dados['hash'], dados['assinatura_digital'], dados['status'])

            resultado = logs.consultar_binario(caminho)
            dados['id_binario'] = resultado["id"]

        processo = logs.consultar_processo(pid)

        if not processo:
            logs.inserir_processo(pid, ppid, nome, "", 0, "", "", dados['id_binario'])

        return dados
    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a análise da ligação de rede. (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "redes", data_atual, erro)
        return {
            'id_binario': 0,
            'caminho': caminho,
            'hash': '',
            'assinatura_digital': '',
            'status': ''
        }

# =========================
# ANÁLISE PRINCIPAL.
# =========================
def verificar_conexoes_de_rede():
    try:
        os.system("cls")
        print("-" * 45 , "\n")
        print("Conexões de rede analisadas: \n")
        print("-" * 45)
        print("\n")

        conexoes = []
        temp = dict()
        ppid = 0

        vistos = set()

        tipos_assinatura = {
            'Valid': 'Válida',
            'NotSigned': 'Sem assinatura',
            'HashMismatch': 'Ficheiro alterado',
            'NotTrusted': 'Certificado inválido',
            'UnknownError': 'Erro na verificação da assinatura digital'
        }

        lista_ips = carregar_lista.carregar_lista("listas/ips_suspeitos.txt")
        lista_dominios = carregar_lista.carregar_lista("listas/dominios_suspeitos.txt")

        for connection in psutil.net_connections(kind='inet'):

            try:
                pid = connection.pid
                caminho = obter_caminho_binario(pid)

                if pid is not None:
                    try:
                        proc = psutil.Process(pid)
                        nome = proc.name()
                        ppid = proc.ppid()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        nome = "Desconhecido"
                else:
                    nome = "Sem PID"

                if connection.raddr:
                    ip_remoto = connection.raddr[0]
                    porta_remota = connection.raddr[1]
                    dominio = obter_dominio(ip_remoto)
                else:
                    ip_remoto = "Sem conexão remota"
                    porta_remota = "Sem porta remota"
                    dominio = "Sem domínio"

                resultado_consulta = verificar_caminho_conexao_rede(
                    caminho, tipos_assinatura, pid, ppid, nome
                )

                temp['ip_local'] = connection.laddr.ip
                temp['porta_local'] = connection.laddr.port
                temp['endereco_remoto'] = ip_remoto
                temp['dominio'] = dominio
                temp['porta_remota'] = porta_remota
                temp['estado'] = connection.status
                temp['pid'] = pid
                temp['nome'] = nome
                temp['caminho'] = resultado_consulta['caminho']
                temp['assinatura'] = resultado_consulta['assinatura_digital']
                temp['status'] = resultado_consulta['status']
                temp['hash'] = resultado_consulta['hash']
                temp['pontuacao'] = 0
                temp['risco'] = ''

                chave = (
                    pid,
                    temp['ip_local'],
                    temp['porta_local'],
                    temp['endereco_remoto'],
                    temp['porta_remota'],
                    temp['estado']
                )

                if chave in vistos:
                    continue

                vistos.add(chave)

                item = calcular_score_conexoes_rede(temp.copy(),lista_ips,lista_dominios)

                temp['pontuacao'] = item[0]['pontuacao']
                temp['risco'] = item[0]['risco']

                motivo = criar_string.criar_string_motivo(item[1])

                conexoes_copia = temp.copy()
                conexoes.append(conexoes_copia)

                mostrar_conexoes([conexoes_copia], item[1])

                id_processo = logs.consultar_processo(pid)

                logs.inserir_conexoes_rede(
                    temp['ip_local'],
                    temp['porta_local'],
                    temp['endereco_remoto'],
                    temp['dominio'],
                    temp['porta_remota'],
                    temp['estado'],
                    temp["pontuacao"],
                    temp["risco"],
                    motivo,
                    id_processo["id"]
                )

            except Exception as e:
                print(f"{cores.CORES['vermelho']}Erro numa conexão (verificar logs){cores.CORES['limpo']}")
                erro = f"{type(e).__name__}: {e}"
                logs.inserir_log_erro("erro", "redes", data_atual, erro)
                continue

    except KeyboardInterrupt:
        print("Processo interrompido pelo utilizador")

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Erro geral nas conexões de rede{cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "redes", data_atual, erro)


def calcular_score_conexoes_rede(conexao, lista_ips, lista_dominios):
    """
    :param conexao: conexão de rede por analisar
    :param lista_ips: lista de ips suspeitos
    :param lista_dominios: lista de dominios suspeitos
    :return: dicionário preenchido com dados
    """
    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    try:
        endereco_remoto = conexao['endereco_remoto'].lower()
        dominio = conexao['dominio'].strip()
        porta = conexao['porta_remota']
        caminho_conexao = conexao['caminho']

        score, motivo = pontos_assinatura.pontos_assinatura(conexao['status'])
        dados_score['pontuacao'] += score
        if (conexao['status'] not in ["Valid", "Sistema"]):
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
    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante o cálculo de score (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "redes", data_atual, erro)
        dados_score['pontuacao'] = 0
        motivos = ["Erro no cálculo de score"]

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos

# =========================
# FUNÇÕES DE EXIBIÇÃO.
# =========================
def mostrar_conexoes(lista, motivos):
    """
    :param lista: lista de conexões de rede
    :param motivos: motivos de cada classificação e pontuação de risco
    :return: lista de conexões de rede
    """
    for conexao in lista:
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"{cores.CORES['azul']}Identificação:{cores.CORES['limpo']}\n")
        print(f"PID do Processo     : {conexao['pid']}")
        print(f"Nome do Processo    : {conexao['nome']}\n")
        print(f"{cores.CORES['amarelo']}Executável:{cores.CORES['limpo']}\n")
        print(f"Caminho processo    : {conexao['caminho']}")
        print(f"Assinatura digital  : {conexao['assinatura']}")
        print(f"Hash do executável  : {conexao['hash']}\n")
        print(f"{cores.CORES['roxo']}Conexão:{cores.CORES['limpo']}\n")
        print(f"IP Local            : {conexao['ip_local']}")
        print(f"Porta Local         : {conexao['porta_local']}")
        print(f"Endereço Remoto     : {conexao['endereco_remoto']}")
        print(f"Porta Remota        : {conexao['porta_remota']}")
        print(f"Estado da Conexão   : {conexao['estado']}\n")
        print(f"{cores.CORES['cyan']}Destino:{cores.CORES['limpo']}\n")
        print(f"Dominio             : {conexao['dominio']}\n")
        print(f"{cores.CORES['verde']}Avaliação:{cores.CORES['limpo']}\n")
        print(f"Pontuação de risco  : {conexao['pontuacao']}")
        print(f"Nível de risco      : {conexao['risco']}")
        print(f"Motivos             : {criar_string.criar_string_motivo(motivos)}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("\n")