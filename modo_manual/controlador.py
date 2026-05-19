import os
import re
import psutil
import winreg
import shlex
import subprocess
from modo_manual import analise_processo as a_processo
from modo_manual import analise_persistencia as a_persistencia
from modulos import interface
from modulos import logs
from modulos import redes as r
from uteis import normalizar_caminho
from uteis import obter_hash
from uteis import calcular_score
from uteis import atribuir_risco
from uteis import pontos_assinatura
from uteis import verificar_assinatura_digital
from uteis import caminho_raiz
from uteis import carregar_lista
from uteis import criar_string
from API import virusTotal

mensagem = "Pressione enter para voltar ao menu do modo manual..."

tipos_assinatura = {'Valid':'Válida', 'NotSigned':'Sem assinatura',
                    'HashMismatch':'Ficheiro alterado', 'NotTrusted':'Certificado inválido',
                    'UnknownError':'Erro na verificação da assinatura digital'}
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

def exibir_resultados_consulta(resultado):
    print("\n")
    os.system("cls")
    print("---------------- Resultados da consulta ----------------")
    if (isinstance (resultado, dict)):
        print(f"Número de motores que indicaram este hash pertecence a uma malware: {resultado["malicious"]}")
        print(f"Número de motores que detectaram comportamento suspeito: {resultado["suspicious"]}")
        print(f"Número de motores que indicaram que este hash pertence a um programa inofensivo: {resultado["harmless"]}")
        print(f"Número de motores que indicaram que não conhecem o hash fornecido: {resultado["undetected"]}")
    else:
        print(resultado)


# =========================
# ANÁLISE PRINCIPAL
# =========================

def analisar_processo():
    a_processo.analisar_processo(tipos_assinatura)

def analisar_programa_chave_registo_HKCU():
    a_persistencia.analisar_programa_chave_registo_HKCU(tipos_assinatura)

def analisar_programa_chave_registo_HKLM():
    a_persistencia.analisar_programa_chave_registo_HKLM(tipos_assinatura)

def analisar_tarefa_agendada():
    a_persistencia.analisar_tarefa_agendada(tipos_assinatura)



def analisar_servico():
    os.system("cls")
    servicos = list()  # lista de servicos ativos.
    ficheiro = carregar_lista.carregar_lista("listas/blacklist_servicos.txt")

    print("Serviços disponíveis para análise: \n")
    try:
        resultado = subprocess.run(["sc", "query", "type=", "service", "state=", "all"],
                                   capture_output=True,
                                   text=True,
                                   encoding="cp850",
                                   check=True)

        blocos = resultado.stdout.strip().split("\n\n")

        for bloco in blocos:
            linhas = bloco.strip().splitlines()
            dados = {}
            for linha in linhas:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip().lower()
                    valor = valor.strip()
                    if chave in ["service_name", "nome_servico"]:
                        dados["nome"] = valor
                        dados["caminho"] = p.caminho_servico(valor)
                    elif chave in ["display_name", "nome_exibido"]:
                        dados["exibido"] = valor
                    elif chave in ["state", "estado"]:
                        dados["estado"] = valor
            if "nome" in dados:
                servicos.append(dados.copy())

        item = selecionar_valor(servicos)

        os.system("cls")

        estado_assinatura = verificar_assinatura_digital.verificar_assinatura(item["caminho"])
        assinatura = tipos_assinatura.get(estado_assinatura, "Assinatura digital desconhecida")
        status = estado_assinatura
        hash = obter_hash.obter_hash(item["caminho"])
        info_score = calcular_score_servicos(ficheiro, item, status)
        pontuacao = info_score[0]['pontuacao']
        risco = info_score[0]['risco']
        motivos = criar_string.criar_string_motivo(info_score[1])

        print("Dados do serviço: ")
        print("-----------------------")
        print(f"Nome do serviço: {item['nome']}")
        print(f"Nome exibido: {item['exibido']}")
        print(f"Caminho: {item['caminho']}")
        print(f"Estado do serviço: {item['estado']}")
        print(f"Hash do executável: {hash}")
        print(f"Estado da assinatura digital: {assinatura}")
        print(f"Pontuação de riscco: {pontuacao}")
        print(f"Nível de risco: {risco}")
        print(f"Motivos: {motivos}")
        print("-----------------------")

    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")

def calcular_score_servicos(ficheiro, servico, status):
    """
    :param lista: corresponde a lista de serviços.
    :param ficheiro: Corresponde a blacklist de serviços maliciosos.
    :return: devolve uma dicionário com as informações dos suspeitos.
    """
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    nome_servico = servico['nome'].lower().strip()
    caminho_servico = normalizar_caminho.normalizar(servico['caminho'])

    score, motivo = pontos_assinatura.pontos_assinatura(status)
    dados_score['pontuacao'] += score
    if (status != "Valid"):
        motivos.append(motivo)

    if ("_" in nome_servico):
        nome_servico = p.nome_base(servico["nome"].strip().lower())

    if (caminho_raiz.verificar_caminho_raiz(caminho_servico)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    score_local, motivos_locais = calcular_score.calcular_score_auxiliar(ficheiro, nome_servico, caminho_servico)

    dados_score['pontuacao'] += score_local['pontuacao']
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos

def analisar_conexao_rede():
    os.system("cls")
    conexoes = list()
    temporario = dict()
    cache_processos = dict()
    cache_dns = dict()
    dominio = ''

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
        temporario['nome'] = nome
        temporario['caminho'] = caminho

        conexoes.append(temporario.copy())

    item = selecionar_valor(conexoes)
    caminho = item['caminho']
    resultado_assinatura = ''
    assinatura = ''
    hash = ''

    os.system("cls")

    if ip_local(item['endereco_remoto']):
        item['dominio'] = "Local"
    else:
        if item['endereco_remoto'] in cache_dns:
            item['dominio'] = cache_dns[item['endereco_remoto']]
        else:
            item['dominio'] = r.obter_dominio(item['endereco_remoto'])
            cache_dns[item['endereco_remoto']] = item['dominio']

    if (caminho.strip() in ['Acesso negado ou processo terminado', '', 'Registry']):
        assinatura = 'Ignorado (Sistema)'
        hash = 'Ignorado (Sistema)'
        status = 'Sistema'

    resultado_assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
    hash = obter_hash.obter_hash(caminho)
    assinatura = tipos_assinatura.get(resultado_assinatura, "Assinatura digital desconhecida")
    status = resultado_assinatura

    info_score = calcular_score_conexoes_rede(item, lista_ips, lista_dominios, status)

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
    print(f"Caminho processo    : {item['caminho']}")
    print(f"Assinatura digital  : {assinatura}")
    print(f"Hash do executável  : {hash}")
    print(f"Pontuação de risco  : {pontuacao}")
    print(f"Nível de risco      : {risco}")
    print(f"Motivos             : {motivos}")
    print("----------------------------------------------")

def calcular_score_conexoes_rede(conexao, lista_ips, lista_dominios, status):

    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    endereco_remoto = conexao['endereco_remoto'].lower()
    dominio = conexao['dominio'].strip()
    porta = conexao['porta_remota']
    caminho_conexao = conexao['caminho']

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

# =========================
# CONSULTA NA API VIRUSTOTAL
# =========================

def consultar_API():
    resultado_consulta = virusTotal.verificar_hash()
    if (resultado_consulta != 0):
        exibir_resultados_consulta(resultado_consulta)

# =========================
# PROCESSOS DB
# =========================

def mostrar_processos_db():
    logs.consultar_processos()

# =========================
# HKCU
# =========================

def mostrar_programas_HKCU_db():
    logs.consultar_programas("HKCU (HKEY_CURRENT_USER)")

# =========================
# HKLM
# =========================

def mostrar_programas_HKLM_db():
    logs.consultar_programas("HKLM (HKEY_LOCAL_MACHINE)")

# =========================
# TAREFAS AGENDADAS
# =========================

def mostrar_tarefas_agendadas_db():
    logs.consultar_tarefas_agendadas()

# =========================
# SERVIÇOS
# =========================

def mostrar_servicos_db():
    logs.consultar_servicos()

# =========================
# CONEXÕES DE REDE
# =========================

def mostrar_conexoes_db():
    logs.consultar_conexoes_rede()


def modo_manual():
    opcoes = {
        1: analisar_processo,
        2: analisar_programa_chave_registo_HKCU,
        3: analisar_programa_chave_registo_HKLM,
        4: analisar_tarefa_agendada,
        5: analisar_servico,
        6: analisar_conexao_rede,
        7: consultar_API,
        8: mostrar_processos_db,
        9: mostrar_programas_HKCU_db,
        10: mostrar_programas_HKLM_db,
        11: mostrar_tarefas_agendadas_db,
        12: mostrar_servicos_db,
        13: mostrar_conexoes_db
    }

    os.system("cls")
    while True:
        opc = interface.menu_modo_manual()
        os.system("cls")
        funcao = opcoes.get(opc)

        if (opc == 14):
            break

        if funcao:
            funcao()
            input("Pressione enter para voltar...")
            os.system("cls")
        else:
            print("Opção inválida")