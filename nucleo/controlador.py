import os
import re
import psutil
import winreg
import shlex
import subprocess
from modulos import interface
from modulos import logs
from modulos import persistencia_arquivos as p
from modulos import redes as r
from uteis import normalizar_caminho
from uteis import obter_hash
from uteis import variaveis_de_ambiente
from uteis import carregar_lista
from uteis import verificar_assinatura_digital
from uteis import caminho_raiz
from uteis import validar_resposta
from acoes import processo
from API import virusTotal

mensagem = "Pressione enter para voltar ao menu do modo manual..."

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

def selecionar_valor(lista):
    i = 0
    for i, binario in enumerate(lista):
        print(f"{i + 1} -> Nome: {binario['nome']}")
    total = i

    while True:
        try:
            opc = int(input(f"Selecione um valor entre 1 e {total + 1}: "))
            if (((opc - 1) > total) or (opc <= 0)):
                print("Selecione uma opção válida!")
            else:
                break
        except (ValueError):
            print("Selecione uma opção válida!")
    return lista[opc - 1]

def selecionar_resposta(dado):
    while True:
        resposta = str(input(f"Deseja verificar se o {dado} é suspeito [Y/N]: ")).upper()
        if (resposta == "Y" or resposta == "N"):
            break
        elif (resposta not in ["Y", "N"]):
            print("Selecione uma resposta válida!")
    return resposta

def exibir_resultados_consulta(resultado):
    print("\n")
    print("---------------- Resultados da consulta ----------------")
    if (isinstance (resultado, dict)):
        print(f"Número de motores que indicaram este hash pertecence a uma malware: {resultado["malicious"]}")
        print(f"Número de motores que detectaram comportamento suspeito: {resultado["suspicious"]}")
        print(f"Número de motores que indicaram que este hash pertence a um programa inofensivo: {resultado["harmless"]}")
        print(f"Número de motores que indicaram que não conhecem o hash fornecido: {resultado["undetected"]}")
    else:
        print(resultado)

def programas_chave_registo(hive, caminho, tabela):
    os.system("cls")
    temporario = dict()
    programas = list()
    try:
        # Abrir chave de registro com permissão de leitura
        chave = winreg.OpenKey(hive, caminho)
        temporario['HK'] = 'HKCU (HKEY_CURRENT_USER)' if hive == winreg.HKEY_CURRENT_USER else 'HKLM (HKEY_LOCAL_MACHINE)'
        i = 0
        while True:
            try:
                nome, valor, tipo = winreg.EnumValue(chave, i)  # lê e atribui os valores da chave de registo
                temporario['nome'] = nome + '.exe'
                argumento = shlex.split(valor, posix=True)
                if ("\\" in argumento[0]):
                    temporario['caminho'] = os.path.expandvars(argumento[0])
                else:
                    temporario['caminho'] = os.path.expandvars(valor)
                temporario['tipo'] = tipo
                programas.append(temporario.copy())
                i += 1
            except OSError:
                break  # Sem mais entradas
        winreg.CloseKey(chave)  # fecha a chave de registo.

        item = selecionar_valor(programas)

        os.system("cls")

        resultado_assinatura = verificar_assinatura_digital.verificar_assinatura(item['caminho'])
        assinatura = "Válida" if resultado_assinatura == "Signature verified." else resultado_assinatura
        hash_programa = obter_hash.obter_hash(item['caminho'])

        print("Dados do programa")
        print("------------------------------------")
        print(f"Nome do programa: {item['nome']}")
        print(f"Caminho: {item['caminho']}")
        print(f"Tipo: {item['tipo']}")
        print(f"Iniciado por: {item['HK']}")
        print(f"Hash do programa: {hash_programa}")
        print(f"Estado da assinatura digital: {assinatura}")
        print("------------------------------------")
    except FileNotFoundError:
        print(f"Chave não encontrada: {caminho}")
    except PermissionError:
        print(f"Acesso negado à chave: {caminho}")

# =========================
# ANÁLISE PRINCIPAL
# =========================

def analisar_processo():
    os.system("cls")
    temporario = dict() # Irá armazenar de forma temporário dados relativos a um processo.
    processos = list() # Irá armazenar os respectivos dados vindos do dicionário temporário.
    print("Processos disponíveis para análise: \n")
    for process in psutil.process_iter(['pid', 'ppid', 'name', 'username', 'exe']):
        try:
            caminho = process.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            caminho = "Acesso negado ou processo terminado"
        temporario['pid'] = process.pid
        temporario['ppid'] = process.ppid()
        temporario['nome'] = process.name()
        temporario['caminho'] = normalizar_caminho.normalizar(caminho)
        temporario['utilizador'] = process.username()

        if (temporario['nome'].endswith(".exe")):
            processos.append(temporario.copy())
    item = selecionar_valor(processos)

    os.system("cls")

    resultado_assinatura = verificar_assinatura_digital.verificar_assinatura(item['caminho'])
    assinatura = "Válida" if resultado_assinatura == "Signature verified." else resultado_assinatura
    hash_processo = obter_hash.obter_hash(item['caminho'])

    print("Dados do binário:")
    print("--------------------")
    print(f"PID: {item['pid']}")
    print(f"PPID: {item['ppid']}")
    print(f"Nome: {item['nome']}")
    print(f"Caminho: {item['caminho']}")
    print(f"Utilizador do processo: {item['utilizador']}")
    print(f"Hash do executável: {hash_processo}")
    print(f"Estado da assinatura digital: {assinatura}")
    print("--------------------")

    resposta = validar_resposta.validar_resposta("Deseja terminar o processo")

    if (resposta in ["SIM", "S"]):
        processo.terminar_processo(item['pid'])


def analisar_programa_chave_registo_HKCU():
    programas_chave_registo(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            "programas_HKCU_suspeitos")

def analisar_programa_chave_registo_HKLM():
    programas_chave_registo(winreg.HKEY_LOCAL_MACHINE,
                            r"Software\Microsoft\Windows\CurrentVersion\Run",
                            "programas_HKLM_suspeitos")

def analisar_tarefa_agendada():

    os.system("cls")
    tarefas_agendadas = list()
    caminho_exe = ""

    print("Tarefas agendadas disponíveis para análise: \n")
    try:
        resultado = subprocess.run(["schtasks", "/query", "/fo", "LIST", "/v"],
                                   capture_output=True,
                                   text=True,
                                   encoding="mbcs",
                                   check=True)
        blocos = re.split(r'\r?\n(?=TaskName:|Nome da tarefa:)', resultado.stdout)
        for bloco in blocos:
            dados = {}
            linhas = bloco.strip().splitlines()
            for linha in linhas:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip().lower()
                    valor = valor.strip()
                    if chave in ["taskname", "nome da tarefa"]:
                        dados["nome"] = valor
                    elif chave in ["next run time", "horário de próxima execução"]:
                        dados["proxima_execucao"] = valor
                    elif chave in ["last run time", "última hora de execução"]:
                        dados["ultima_execucao"] = valor
                    elif chave in ["task to run", "tarefa a executar", "action", "ação"]:
                        if ".exe" in valor.lower():
                            m = re.match(r'[\S ]+\.exe[ "]', valor)
                            if m:
                                m = re.match(r'[\S ]+\.exe[ "]', valor)
                                caminho_exe = os.path.expandvars(m.group(0).strip('"').strip())
                                dados['tarefa_executada'] = caminho_exe
                            else:
                                caminho_exe = os.path.expandvars(valor)
                        else:
                            if (valor == "COM handler"):
                                dados['tarefa_executada'] = valor
                            else:
                                bruto = valor
                                argumentos = shlex.split(bruto, posix=False)
                                if argumentos:
                                    caminho_exe = argumentos[0].strip('"')
                                    caminho_exe = os.path.expandvars(caminho_exe)
                                    dados['tarefa_executada'] = caminho_exe

                    elif chave in ["run as user", "executar como usuário"]:
                        dados["utilizador"] = valor
            if "nome" in dados:
                tarefas_agendadas.append(dados.copy())

        item = selecionar_valor(tarefas_agendadas)

        os.system("cls")

        if (item['tarefa_executada'] != 'COM handler'):
            resultado_assinatura = verificar_assinatura_digital.verificar_assinatura(item['tarefa_executada'])
            assinatura = "Válida" if resultado_assinatura == "Signature verified." else resultado_assinatura
            hash = obter_hash.obter_hash(item['tarefa_executada'])
        else:
            hash = "N/A"
            assinatura = "N/A"

        print("Dados da tarefa agendada: ")
        print("-----------------------------")
        print(f"Nome: {item['nome']}")
        print(f"Última execução: {item['ultima_execucao']}")
        print(f"Proxima execução: {item['proxima_execucao']}")
        print(f"Caminho: {item['tarefa_executada']}")
        print(f"Utilizador: {item['utilizador']}")
        print(f"Hash do executável: {hash}")
        print(f"Estado da assinatura digital: {assinatura}")
        print("-----------------------------")

    except FileNotFoundError:
        print("ERRO: O comando 'schtasks' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")


def analisar_servico():
    os.system("cls")
    servicos = list()  # lista de servicos ativos.

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

        if (os.path.exists(item["caminho"]) and item["caminho"].lower().strip().endswith(".exe")):
            estado_assinatura = verificar_assinatura_digital.verificar_assinatura(item["caminho"])
            assinatura = "Válida" if estado_assinatura == "Signature verified." else estado_assinatura
            hash = obter_hash.obter_hash(item["caminho"])
        else:
            assinatura = "Não foi possível verificar a assinatura digital (caminho inválido ou não encontrado)"
            hash = "Não foi possivel obter o hash (caminho inválido ou não encontrado)"

        print("Dados do serviço: ")
        print("-----------------------")
        print(f"Nome do serviço: {item['nome']}")
        print(f"Nome exibido: {item['exibido']}")
        print(f"Caminho: {item['caminho']}")
        print(f"Estado do serviço: {item['estado']}")
        print(f"Hash do executável: {hash}")
        print(f"Estado da assinatura digital: {assinatura}")
        print("-----------------------")

    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")


def analisar_conexao_rede():
    os.system("cls")
    conexoes = list()
    temporario = dict()
    cache_processos = dict()
    cache_dns = dict()
    dominio = ''

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

    if (os.path.exists(caminho) and caminho.lower().endswith('.exe')):
        resultado_assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
        hash = obter_hash.obter_hash(caminho)
        assinatura = "Válida" if resultado_assinatura == "Signature verified." else resultado_assinatura
    else:
        if (item['pid'] != 0 and item['pid'] != 4):
            temporario['assinatura'] = 'Erro ao obter assinatura digital (caminho inválido ou inexistente)'
            temporario['hash'] = 'Erro ao obter hash (caminho inválido ou inexistente)'

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
    print("----------------------------------------------")


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