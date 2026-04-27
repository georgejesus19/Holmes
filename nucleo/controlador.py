import os
import re
import psutil
import winreg
import shlex
import subprocess
import socket
from pathlib import Path
from modulos import interface
from modulos import logs
from uteis import normalizar_caminho
from uteis import obter_hash
from uteis import variaveis_de_ambiente
from uteis import carregar_lista
from uteis import verificar_assinatura_digital
from modulos.API import virusTotal

mensagem = "Pressione enter para voltar ao menu do modo manual..."

# =========================
# FUNÇÕES AUXILIARES.
# =========================

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

def obter_camainho_binario(pid):
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

def nome_base(servico):
    """
    :param servico: nome do serviço em questão
    :return: devolce o servico (ignorando o identificador [vem depois do "_"]
    """
    return servico.split("_")[0].strip().lower()

def verificar_caminho_raiz(caminho):
    p = Path(caminho)
    # parent como string e normalize para barras
    parent_str = str(p.parent).replace("/", "\\")
    return (p.suffix.lower() == ".exe" and parent_str == p.anchor)

def caminho_servico(nome):
    """
    :param nome: Recebe o nome de um processo.
    :return: Devolve o caminho do processo.
    """
    caminho = ""
    try:
        resultado = subprocess.run(["sc", "qc", nome],
                                   capture_output=True,
                                   text=True,
                                   check=True)

        blocos = resultado.stdout.strip().split("\n\n")

        for bloco in blocos:
            linhas = bloco.strip().splitlines()
            for linha in linhas:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip().lower()
                    valor = valor.strip()
                    if chave in ["binary_path_name", "nome_caminho_binario"]:
                        caminho = valor.strip('"')
                        if (caminho.lower().endswith(".exe") == False):
                            caminho = caminho.split(".exe")[0] + ".exe"
                        caminho = os.path.normpath(caminho)
        return caminho
    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
        return ""
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
        return ""
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
        return ""

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

        resposta = selecionar_resposta("programa")

        if (resposta == "Y"):
            blacklist = carregar_lista.carregar_lista("listas/blacklist.txt")
            nome_programa = item['nome'].lower().strip()
            caminho_programa = normalizar_caminho.normalizar(item['caminho'])
            suspeito = False

            for valor_programa in blacklist:
                if (nome_programa == valor_programa) or \
                        (caminho_programa.startswith(variaveis_de_ambiente.expandir_caminhos(valor_programa))):
                    if (assinatura != "Válida"):
                        suspeito = True
                    break
            if (suspeito):
                print(f"O programa {nome_programa} foi considerado suspeito!")
                logs.inserir_programas_chave_registo(item['nome'], item['caminho'],
                                                     item['tipo'], item['HK'],
                                                     assinatura, hash_programa,
                                                     tabela)
            else:
                print(f"O programa {nome_programa} não foi considerado suspeito!")
    except FileNotFoundError:
        print(f"Chave não encontrada: {caminho}")
    except PermissionError:
        print(f"Acesso negado à chave: {caminho}")

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

def obter_dominio(endereco_ip):
    try:
        dominio = socket.gethostbyaddr(endereco_ip)[0]
    except (socket.herror, socket.gaierror) as erro:
        dominio = "Desconhecido"
    return dominio

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

def ip_local(ip):
    return (
        ip.startswith("127.") or
        ip.startswith("192.168.") or
        ip.startswith("10.") or
        ip.startswith("172.") or
        ip == "::1"
    )
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

    resposta = selecionar_resposta("processo")

    if (resposta == "Y"):
        blacklist = carregar_lista.carregar_lista("listas/blacklist.txt")
        nome_processo = item['nome'].lower().strip()
        caminho_processo = normalizar_caminho.normalizar(item['caminho'])
        suspeito = False
        for valor_processo in blacklist:
            if (valor_processo == nome_processo) or \
                (caminho_processo.startswith(variaveis_de_ambiente.expandir_caminhos(valor_processo))):
                if (assinatura != "Válida"):
                    suspeito = True
                break
        if (suspeito):
            print(f"O processo {item['nome']} foi considerado suspeito!")
            logs.inserir_processo(item['pid'], item['ppid'], item['nome'], item['caminho'],
                                  item['utilizador'], item['hash'], item['assinatura'], "processos_suspeitos")
        else:
            print(f"O processo {item['nome']} não foi considerado suspeito!")


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

        resposta = selecionar_resposta("Tarefa agendada")

        if (resposta == "Y"):
            blacklist = carregar_lista.carregar_lista("listas/blacklist.txt")
            nome_tarefa = os.path.basename(item['tarefa_executada'])
            caminho_tarefa = normalizar_caminho.normalizar(item['tarefa_executada'])
            suspeito = False

            for valor_tarefa_agendade in blacklist:
                # Comparação
                if (valor_tarefa_agendade == nome_tarefa or \
                   (caminho_tarefa.startswith(variaveis_de_ambiente.expandir_caminhos(valor_tarefa_agendade)))):
                    if ((assinatura != "Válida" and item['tarefa_executada'] != "COM handler")):
                        suspeito = True

            if (suspeito):
                print(f"A tarefa agendada {item['nome']} foi considerada suspeita")
                logs.inserir_tarefas_agendadas(item['nome'], item['proxima_execucao'],
                                               item['ultima_execucao'], item['tarefa_executada'],
                                               item['utilizador'], item['hash'],
                                               item['assinatura'], "tarefas_agendadas_suspeitas")
            else:
                print(f"A tarefa agendada {item['nome']} não foi considerada suspeita")

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
                        dados["caminho"] = caminho_servico(valor)
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

        resposta = selecionar_resposta("Serviços")

        if (resposta == "Y"):
            blacklist_servicos = carregar_lista.carregar_lista("listas/blacklist_servicos.txt")
            nome_servico = item['nome'].strip().lower()
            caminho = normalizar_caminho.normalizar(item['caminho'])
            suspeito = False

            if ("_" in nome_servico):
                nome_servico = nome_base(item['nome'].strip().lower())
            for valor_servico in blacklist_servicos:
                if (nome_servico == valor_servico) or \
                   (caminho.startswith(variaveis_de_ambiente.expandir_caminhos(caminho))) or \
                   (verificar_caminho_raiz(caminho)):
                    if (assinatura != "Válida"):
                        suspeito = True
                    break

            if (suspeito):
                print(f"O serviço {item['nome']} foi considerado suspeito.")
                logs.inserir_servicos(item['nome'], item['exibido'],
                                      item['estado'], item['caminho'],
                                      item['assinatura'], item['hash'],
                                      "servicos_suspeitos")
            else:
                print(f"O serviço {item['nome']} não foi considerado suspeito.")
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
                    caminho = obter_caminho_binario(pid)
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
            item['dominio'] = obter_dominio(item['endereco_remoto'])
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

    resposta = selecionar_resposta("Conexão de rede")

    if (resposta == "Y"):

        PORTAS_SUSPEITAS = {20, 21, 22, 23, 25, 53, 80, 110, 143,
                            445, 3306, 3389, 8080, 4444, 5555,
                            6666, 6667, 12345, 27374, 31337}

        TLDs_SUSPEITAS = {".tk", ".ml", ".ga", ".cf", ".gq",
                          ".top", ".xyz", ".monster", ".cyou",
                          ".club", ".click", ".support"}

        dominios_suspeitos = carregar_lista.carregar_lista("listas/dominios_suspeitos.txt")
        ips_suspeitos = carregar_lista.carregar_lista("listas/ips_suspeitos.txt")
        suspeito = False


        endereco_remoto = item['endereco_remoto'].lower()
        dominio = item['dominio'].strip()
        porta = item['porta_remota']

        # verifica se é suspeito
        if (endereco_remoto in ips_suspeitos) or \
            (verificar_tld(dominio, TLDs_SUSPEITAS)) or \
            (verificar_dominio(dominio, dominios_suspeitos)) or \
            (verificar_porta(porta, PORTAS_SUSPEITAS)):
            if (item['assinatura'] not in ["Válida", "Ignorado (Sistema)"]):
                suspeito = True

        if (suspeito):
            print(f"A conexão de rede efetuada pelo processo {item['nome']} foi considerada suspeita.")
            logs.inserir_conexoes_rede(item['ip_local'], item['porta_local'],
                                        item['endereco_remoto'], item['dominio'],
                                        item['porta_remota'], item['estado'],
                                        item['pid'], item['nome'], item['assinatura'],
                                        "conexoes_rede_suspeitas")
        else:
            print(f"A conexão de rede efetuada pelo processo {item['nome']} não foi considerada suspeita.")

# =========================
# CONSULTA NA API VIRUSTOTAL
# =========================

def consultar_API():
    resultado_consulta = virusTotal.verificar_hash()
    print(resultado_consulta)

# =========================
# PROCESSOS DB
# =========================

def mostrar_processos_db():
    logs.consultar_processos("processos")
    input(mensagem)
    os.system("cls")

def mostrar_processos_suspeitos_db():
    logs.consultar_processos("processos_suspeitos")
    input(mensagem)
    os.system("cls")


# =========================
# HKCU
# =========================

def mostrar_programas_HKCU_db():
    logs.consultar_programas("programas_HKCU")
    input(mensagem)
    os.system("cls")

def mostrar_programas_suspeitos_HKCU_db():
    logs.consultar_programas("programas_HKCU_suspeitos")
    input(mensagem)
    os.system("cls")

# =========================
# HKLM
# =========================

def mostrar_programas_HKLM_db():
    logs.consultar_programas("programas_HKLM")
    input(mensagem)
    os.system("cls")

def mostrar_programas_suspeitos_HKLM_db():
    logs.consultar_programas("programas_HKLM_suspeitos")
    input(mensagem)
    os.system("cls")

# =========================
# TAREFAS AGENDADAS
# =========================

def mostrar_tarefas_agendadas_db():
    logs.consultar_tarefas_agendadas("tarefas_agendadas")
    input(mensagem)
    os.system("cls")

def mostrar_tarefas_agendadas_suspeitas_db():
    logs.consultar_tarefas_agendadas("tarefas_agendadas_suspeitas")
    input(mensagem)
    os.system("cls")

# =========================
# SERVIÇOS
# =========================

def mostrar_servicos_db():
    logs.consultar_servicos("servicos")
    input(mensagem)
    os.system("cls")

def mostrar_servicos_suspeitos_db():
    logs.consultar_servicos("servicos_suspeitos")
    input(mensagem)
    os.system("cls")


# =========================
# CONEXÕES DE REDE
# =========================

def mostrar_conexoes_db():
    logs.consultar_conexoes_rede("conexoes_rede")
    input(mensagem)
    os.system("cls")

def mostrar_conexoes_suspeitas_db():
    logs.consultar_conexoes_rede("conexoes_rede_suspeitas")
    input(mensagem)
    os.system("cls")

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
        9: mostrar_processos_suspeitos_db,
        10: mostrar_programas_HKCU_db,
        11: mostrar_programas_suspeitos_HKCU_db,
        12: mostrar_programas_HKLM_db,
        13: mostrar_programas_suspeitos_HKLM_db,
        14: mostrar_tarefas_agendadas_db,
        15: mostrar_tarefas_agendadas_suspeitas_db,
        16: mostrar_servicos_db,
        17: mostrar_servicos_suspeitos_db,
        18: mostrar_conexoes_db,
        19: mostrar_conexoes_suspeitas_db,
    }

    os.system("cls")
    while True:
        opc = interface.menu_modo_manual()
        os.system("cls")
        funcao = opcoes.get(opc)

        if (opc == 20):
            break

        if funcao:
            funcao()
            input("Pressione enter para voltar...")
            os.system("cls")
        else:
            print("Opção inválida")