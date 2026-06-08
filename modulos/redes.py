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

def verificar_caminho_conexao_rede(caminho, tipos_assinatura, pid, ppid, nome):

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
        logs.inserir_log_erro("erro", "redes", f"{type(e).__name__}: {e}")
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
        print("Conexões de rede analisadas: \n")
        conexoes = list()
        temp = dict()
        ppid = 0

        tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                            'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                            'UnknownError': 'Erro na verificação da assinatura digital'}

        lista_ips = carregar_lista.carregar_lista("listas/ips_suspeitos.txt")
        lista_dominios = carregar_lista.carregar_lista("listas/dominios_suspeitos.txt")

        for connection in psutil.net_connections(kind='inet'):
            try:
                pid = connection.pid
                caminho = obter_caminho_binario(pid)
                # Nome do processo
                if pid is not None:
                    try:
                        proc = psutil.Process(pid)
                        nome = proc.name()
                        ppid = proc.ppid()
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

                resultado_consulta = verificar_caminho_conexao_rede(caminho, tipos_assinatura, pid, ppid, nome)

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

                item = calcular_score_conexoes_rede(temp.copy(), lista_ips, lista_dominios)
                temp['pontuacao'] = item[0]['pontuacao']
                temp['risco'] = item[0]['risco']
                motivo = criar_string.criar_string_motivo(item[1])
                conexoes_copia = temp.copy()
                conexoes.append(conexoes_copia)
                mostrar_conexoes([conexoes_copia], item[1])

                id_processo = logs.consultar_processo(pid)
                logs.inserir_conexoes_rede(temp['ip_local'], temp['porta_local'], temp['endereco_remoto'],
                                           temp['dominio'], temp['porta_remota'], temp['estado'], temp["pontuacao"],
                                           temp["risco"], motivo, id_processo["id"])
            except Exception as e:
                print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a análise de uma conexão de rede (verificar logs de erro){cores.CORES['limpo']}")
                erro = f"{type(e).__name__}: {e}"
                logs.inserir_log_erro("erro", "redes", erro)
                continue
    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a análise (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "redes", erro)


def calcular_score_conexoes_rede(conexao, lista_ips, lista_dominios):

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
        logs.inserir_log_erro("erro", "redes", f"{type(e).__name__}: {e}")
        dados_score['pontuacao'] = 0
        motivos = ["Erro no cálculo de score"]

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

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