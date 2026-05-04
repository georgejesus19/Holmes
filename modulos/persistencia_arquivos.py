import winreg
import subprocess
import os
import time
import shlex
import re
from modulos import logs
from uteis import obter_hash
from uteis import verificar_assinatura_digital
from uteis import variaveis_de_ambiente
from uteis import normalizar_caminho
from uteis import pontos_assinatura
from uteis import caminho_raiz
from uteis import carregar_lista


# =========================
# FUNÇÕES AUXILIARES.
# =========================

def tipo_caminho(caminho):
    """
    Determina o tipo de ficheiro com base no caminho fornecido, distinguindo entre executáveis normais,
    aplicações da Microsoft Store (WindowsApps) e caminhos inválidos, permitindo aplicar o tratamento adequado.

    :param caminho: Caminho do executável
    :return: Devolve o tipo de caminho
    """
    caminho = caminho.lower()

    # não existe
    if not os.path.exists(caminho):
        return "invalido"

    # não é executável
    if not caminho.endswith(".exe"):
        return "nao_exe"

    # apps da Microsoft Store
    if "windowsapps" in caminho:
        return "store"

    # executável normal
    return "normal"

def analisar_normal(temp, tipos_assinatura):
    temp['hash'] = obter_hash.obter_hash(temp["caminho"])
    assinatura = verificar_assinatura_digital.verificar_assinatura(temp['caminho'])

    temp['status'] = assinatura
    temp['assinatura'] = tipos_assinatura.get(assinatura, "Desconhecida")
    return temp

def tratar_store(temp):
    temp['hash'] = "Não aplicável (Store App)"
    temp['assinatura'] = "Microsoft Store App"
    temp['status'] = "StoreApp"
    return temp

def tratar_invalido(temp):
    temp['hash'] = "Erro"
    temp['assinatura'] = "Caminho inválido"
    temp['status'] = "Invalid"
    return temp

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
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")

def nome_base(servico):
    """
    :param servico: nome do serviço em questão
    :return: devolce o servico (ignorando o identificador [vem depois do "_"]
    """
    return servico.split("_")[0].strip().lower()

# =========================
# FUNÇÕES PRINCIPAIS.
# =========================

#  PROGRAMAS NA CHAVE DE REGISTO:
def ler_chave_run(hive, caminho):
    """
    :param hive: arquivo de configurações do windows.
    :param caminho: caminho da chave de registo.
    :return: todos os programas configurados para arrancar mesmo após reinicialização.
    """
    programas = list()  # guarda os programas todos.
    temp = dict()  # dicionário temporário para guardar info dos programas.
    assinatura = ""
    tabela = ""
    tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                        'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                        'UnknownError': 'Erro na verificação da assinatura digital'}
    lista = carregar_lista.carregar_lista("listas/blacklist.txt")

    try:
        # Abrir chave de registro com permissão de leitura
        hive_nome = 'HKCU (HKEY_CURRENT_USER)' if hive == winreg.HKEY_CURRENT_USER else 'HKLM (HKEY_LOCAL_MACHINE)'
        tabela = "programas_HKCU" if hive_nome == "HKCU (HKEY_CURRENT_USER)" else "programas_HKLM"
        chave = winreg.OpenKey(hive, caminho)
        temp['HK'] = hive_nome  # armazena a configuração HKCU (utilizador atual) ou HKLM (sistema)
        i = 0
        while True:
            try:
                nome, valor, tipo = winreg.EnumValue(chave, i)  # lê e atribui os valores da chave de registo
                temp['nome'] = nome + '.exe'
                argumento = shlex.split(valor, posix=True)
                if ("\\" in argumento[0]):
                    temp['caminho'] = os.path.expandvars(argumento[0])
                else:
                    temp['caminho'] = os.path.expandvars(valor)
                temp['tipo'] = tipo
                temp['assinatura'] = ''
                temp['hash'] = ''
                temp['status'] = ''
                temp['pontuacao'] = 0
                temp['risco'] = ''

                tipo = tipo_caminho(temp['caminho'])

                if (tipo == "normal"):
                    temp = analisar_normal(temp.copy(), tipos_assinatura)
                elif (tipo == "store"):
                    temp = tratar_store(temp.copy())
                else:
                    temp = tratar_invalido(temp.copy())

                item = programas_suspeitos(temp.copy(), lista, hive_nome)

                temp['pontuacao'] = item[0]['pontuacao']
                temp['risco'] = item[0]['risco']

                programas_copia = temp.copy()
                programas.append(programas_copia)
                mostrar_programas_chave_registo([programas_copia], item[1])
                i += 1
            except OSError:
                break  # Sem mais entradas
        winreg.CloseKey(chave)  # fecha a chave de registo.
    except FileNotFoundError:
        print(f"Chave não encontrada: {caminho}")
    except PermissionError:
        print(f"Acesso negado à chave: {caminho}")


def programas_suspeitos(programa, ficheiro, responsavel):
    """
    :param lista: lista de programas numa chave de registo (normalmente lista de dicionários).
    :param ficheiro: blacklist utilizada para comparação.
    :param responsavel: HKCU (utilizador atual) ou HKLM (sistema)
    :return:
    """

    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    score_local = 0
    motivos_locais = []

    nome_achado = False
    caminho_achado = False
    nome_presente = False
    caminho_presente = False

    nome_programa = programa['nome'].lower().strip()
    caminho_programa = normalizar_caminho.normalizar(programa['caminho'])

    score, motivo = pontos_assinatura.pontos_assinatura(programa['status'])
    dados_score['pontuacao'] += score
    if (programa['status'] != "Valid"):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_programa)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    for valor_programa in ficheiro:

        valor_programa = valor_programa.lower().strip()

        if not nome_achado:
            if (valor_programa == nome_programa):
                nome_achado = True
                nome_presente = True

        if not caminho_achado:
            if (caminho_programa.startswith(variaveis_de_ambiente.expandir_caminhos(valor_programa))):
                caminho_achado = True
                caminho_presente = True

            if (nome_presente and caminho_presente):
                score_local = 60
                motivos_locais = ["Nome e caminho presentes na blacklist"]
                break

            elif (nome_presente):
                score_local = 40
                motivos_locais = ["Nome presente na blacklist"]

            elif (caminho_presente):
                score_local = 40
                motivos_locais = ["Caminho presente na blacklist"]

    dados_score['pontuacao'] += score_local
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))

    if (dados_score['pontuacao'] >= 0 and dados_score['pontuacao'] <= 30):
        dados_score['risco'] = 'Baixo'
    elif (dados_score['pontuacao'] > 30 and dados_score['pontuacao'] <= 60):
        dados_score['risco'] = 'Médio'
    else:
        dados_score['risco'] = 'Alto'

    return dados_score, motivos

def obter_HKCU():
    os.system("cls")
    print("Programas na chave de registo (HKCU): ")
    ler_chave_run(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
    input("Pressione enter para continuar...")
    os.system("cls")


def obter_HKLM():
    os.system("cls")
    print("Programas na chave de registo (HKLM): ")
    ler_chave_run(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    input("Pressione enter para continuar...")
    os.system("cls")


# TAREFAS AGENDADAS:
def listar_tarefas_agendadas():
    """
    :return: Devolve todas as tarefas agendadas no windows.
    """
    os.system("cls")
    tarefas = []  # lista de tarefas agendadas
    tarefas_copia = []
    item = []
    tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                        'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                        'UnknownError': 'Erro na verificação da assinatura digital'}
    lista = carregar_lista.carregar_lista("listas/blacklist.txt")

    print("Tarefas em análise: \n")
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
                                assinatura = verificar_assinatura_digital.verificar_assinatura(caminho_exe)
                                dados['hash'] = obter_hash.obter_hash(caminho_exe)
                                dados['tarefa_executada'] = caminho_exe
                                dados['status'] = assinatura
                                dados['assinatura'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")
                            else:
                                caminho_exe = os.path.expandvars(valor)
                                assinatura = verificar_assinatura_digital.verificar_assinatura(caminho_exe)
                                dados['hash'] = obter_hash.obter_hash(caminho_exe)
                                dados['tarefa_executada'] = caminho_exe
                                dados['status'] = assinatura
                                dados['assinatura'] =  tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")
                        else:
                            if (valor == "COM handler"):
                                dados['tarefa_executada'] = valor
                                dados['assinatura'] = "Válida"
                                dados['hash'] = "N/A"
                                dados['status'] = "N/A"
                            else:
                                bruto = valor
                                argumentos = shlex.split(bruto, posix=False)
                                if argumentos:
                                    caminho = argumentos[0].strip('"')
                                    caminho = os.path.expandvars(caminho)
                                    assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
                                    dados['tarefa_executada'] = caminho
                                    dados['hash'] = obter_hash.obter_hash(caminho)
                                    dados['status'] = assinatura
                                    dados['assinatura'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")
                    elif chave in ["run as user", "executar como usuário"]:
                        dados["utilizador"] = valor


            dados['pontuacao'] = 0
            dados['risco'] = ''
            if "tarefa_executada" in dados:
                item = tarefas_suspeitas(dados.copy(), lista)
                dados['pontuacao'] = item[0]['pontuacao']
                dados['risco'] = item[0]['risco']

            if "nome" in dados:
                tarefas_copia = dados.copy()
                tarefas.append(tarefas_copia)
                if (dados['pontuacao'] > 0):
                    obter_tarefas_agendadas([tarefas_copia], item[1])

    except FileNotFoundError:
        print("ERRO: O comando 'schtasks' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")

def tarefas_suspeitas(tarefa, ficheiro):
    """
    :param lista_tarefas: Lista de tarefas agendadas (retorno da função anterior).
    :param ficheiro: A blackklist utilizada como parâmetro de comparação.
    :return: devolve uma lista com as tarefas consideradas suspeitas.
    """
    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    score_local = 0
    motivos_locais = []

    nome_achado = False
    caminho_achado = False
    nome_presente = False
    caminho_presente = False

    valor_tarefa = tarefa['tarefa_executada']

    nome_tarefa = os.path.basename(valor_tarefa)
    caminho_tarefa = normalizar_caminho.normalizar(valor_tarefa)

    score, motivo = pontos_assinatura.pontos_assinatura(tarefa['status'])
    dados_score['pontuacao'] += score
    if (tarefa['status'] != "Valid"):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_tarefa)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    for valor_tarefa in ficheiro:

        valor_tarefa = valor_tarefa.lower().strip()

        if not nome_achado:
            if (valor_tarefa == nome_tarefa):
                nome_presente = True
                nome_achado = True

        if not caminho_achado:
            if (caminho_tarefa.startswith(variaveis_de_ambiente.expandir_caminhos(valor_tarefa))):
                caminho_presente = True
                caminho_achado = True

        if (nome_presente and caminho_presente):
            score_local = 60
            motivos_locais = ["Nome e caminho presentes na blacklist"]
            break

        elif (nome_presente):
            score_local = 40
            motivos_locais = ["Nome presente na blacklist"]

        elif (caminho_presente):
            score_local = 40
            motivos_locais = ["Caminho presente na blacklist"]

    dados_score['pontuacao'] += score_local
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))

    if (dados_score['pontuacao'] >= 0 and dados_score['pontuacao'] <= 30):
        dados_score['risco'] = 'Baixo'
    elif (dados_score['pontuacao'] > 30 and dados_score['pontuacao'] <= 60):
        dados_score['risco'] = 'Médio'
    else:
        dados_score['risco'] = 'Alto'

    return dados_score, motivos

# SERVIÇOS:
def verificar_servicos_ativos(mostrar=True):
    """
    :return: Devolve todos os serviços ativos.
    """
    os.system("cls")
    print("Serviços em análise: \n")
    servicos = []  # lista de servicos ativos.
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
                        if not mostrar:
                            print(f"Em analise: {dados["nome"]}")
                        dados["caminho"] = caminho_servico(valor)
                    elif chave in ["display_name", "nome_exibido"]:
                        dados["exibido"] = valor
                    elif chave in ["state", "estado"]:
                        dados["estado"] = valor
                    if (os.path.exists(dados["caminho"]) and dados["caminho"].lower().strip().endswith(".exe")):
                        estado_assinatura = verificar_assinatura_digital.verificar_assinatura(dados["caminho"])
                        dados['hash'] = obter_hash.obter_hash(dados["caminho"])
                        if (estado_assinatura == "Signature verified."):
                            dados["assinatura"] = "Válida"
                        else:
                            dados["assinatura"] = estado_assinatura
                    else:
                        dados["assinatura"] = "Caminho inválido ou não encontrado."
                        dados["hash"] = "Não foi possivel obter o hash (caminho inválido ou não encontrado)"
            if "nome" in dados:
                servicos.append(dados.copy())
                logs.inserir_servicos(dados['nome'], dados['exibido'],
                                      dados['estado'], dados['caminho'],
                                      dados['assinatura'], dados['hash'], "servicos")

            if mostrar:
                obter_servicos([dados.copy()])
        return servicos
    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")

def verificar_servicos_suspeitos(ficheiro, lista):
    """
    :param lista: corresponde a lista de serviços.
    :param ficheiro: Corresponde a blacklist de serviços maliciosos.
    :return: devolve uma dicionário com as informações dos suspeitos.
    """
    os.system("cls")
    suspeitos = []
    caminhos = set()

    for servico in lista:

        caminho_servico = normalizar_caminho.normalizar(servico["caminho"])
        nome_servico = servico["nome"].strip().lower()

        if ("_" in nome_servico):
            nome_servico = nome_base(servico["nome"].strip().lower())

        if (servico['assinatura'] == "Válida"):
            continue

        if (verificar_caminho_raiz(caminho_servico)):
            if (caminho_servico not in caminhos):
                suspeitos.append({
                    "nome": servico["nome"],
                    "caminho": servico["caminho"],
                    "exibido": servico["exibido"],
                    "estado": servico["estado"],
                    "assinatura": servico["assinatura"],
                    "hash": servico["hash"]
                })
                logs.inserir_servicos(servico['nome'], servico['exibido'],
                                      servico['estado'], servico['caminho'],
                                      servico['assinatura'], servico['hash'],
                                      "servicos_suspeitos")
                caminhos.add(caminho_servico)
            continue

        for exec_servico in ficheiro:
            if ((nome_servico == exec_servico) or \
               (caminho_servico.startswith(variaveis_de_ambiente.expandir_caminhos(exec_servico)))):
                if (caminho_servico not in caminhos):
                    suspeitos.append({
                        "nome": servico["nome"],
                        "caminho": servico["caminho"],
                        "exibido": servico["exibido"],
                        "estado": servico["estado"],
                        "assinatura": servico["assinatura"],
                        "hash": servico["hash"]
                    })
                    logs.inserir_servicos(servico['nome'], servico['exibido'],
                                          servico['estado'], servico['caminho'],
                                          servico['assinatura'], servico['hash'],
                                          "servicos_suspeitos")
                    caminhos.add(caminho_servico)
    os.system("cls")
    tamanho = len(suspeitos)
    if (tamanho > 0):
        print("Serviços suspeitos detetados !")
        resposta = validar_resposta.validar_resposta()
        if (resposta in ["SIM", "S"]):
            logs.consultar_servicos("servicos_suspeitos")
    else:
        print("Não existem serviços suspeitos\n")

# MONITORIZAÇÃO DA PASTA STARTUP:
def monitorar_pasta_startup(tempo=5):
    """
    :param quantidade: define a quantidade de vezes que a varredura sera feita a pasta.
    :param tempo: Tempo pedido para monitoramento da pasta (em segundos) [é um parâmetro opcional].
    :return: devolve a lista das coisas adicionadas ou removidas.
    """
    os.system("cls")
    startup_caminho = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    ficheiros_anteriores = set(os.listdir(startup_caminho))

    adicionados = []
    removidos = []

    print("Iniciando o monitoramento da pasta Startup:")
    try:
        time.sleep(tempo)  # verifica a cada n segundos
        ficheiros_atuais = set(os.listdir(startup_caminho))
        adicionado = ficheiros_atuais - ficheiros_anteriores
        removido = ficheiros_anteriores - ficheiros_atuais

        if adicionado:
            print(f"Novos ficheiros: {adicionado}")
            adicionados.append(adicionado)
        if removido:
            print(f"Ficheiros removidos: {removido}")
            removidos.append(removido)
        if not adicionado and not removido:
            print("Nenhuma alteração detectada, desde a última monitorização.")
        ficheiros_anteriores = ficheiros_atuais
        input("Pressione enter para sair...")
        os.system("cls")

        return adicionados, removidos
    except KeyboardInterrupt:
        print("Monitoramento encerrado")


# =========================
# FUNÇÕES DE EXIBIÇÃO.
# =========================

def mostrar_programas_chave_registo(lista, motivos):
    """
    :param lista: recebe a lista dos programas
    :return: devlolve os programas suspeitos (na chave de registo)
    """
    tamanho = len(lista)
    if (tamanho > 0):
        for programa in lista:
            print("------------------------------------------------------------")
            print(f"Nome                   : {programa.get('nome')}")
            print(f"Caminho                : {programa.get('caminho')}")
            print(f"Tipo                   : {programa.get('tipo')}")
            print(f"Iniciado por           : {programa.get('HK')}")
            print(f"Estado da assinatura   : {programa.get('assinatura')}")
            print(f"Hash                   : {programa.get('hash')}")
            print(f"Pontuação de risco     : {programa.get('pontuacao')}")
            print(f"Nível de risco         : {programa.get('risco')}")
            print("------------------------------------------------------------")
    if (len(motivos) > 0):
        print("Motivos: ")
        for motivo in motivos:
            print(f" - {motivo}")
    print("\n")


def obter_tarefas_agendadas(lista, motivos):
    """
    :param lista: lista das tarefas agendadas.
    :param texto: Diz se estamos a listar a tarefas ou procurar tarefas suspeitas.
    :return: todas as tarefas agendadas ou consideradas suspeitas.
    """
    for linha in lista:
        print("------------------------------------------------------------")
        print(f"Nome                    : {linha.get('nome')}")
        print(f"Próxima Execução        : {linha.get('proxima_execucao')}")
        print(f"Última Execução         : {linha.get('ultima_execucao')}")
        print(f"Tarefa Executada        : {linha.get('tarefa_executada')}")
        print(f"Utilizador              : {linha.get('utilizador')}")
        print(f"Estado da assinatura    : {linha.get('assinatura')}")
        print(f"Hash                    : {linha.get('hash')}")
        print(f"Pontuação de risco      : {linha.get('pontuacao')}")
        print(f"Nível de risco:         : {linha.get('risco')}")
        print("------------------------------------------------------------")
    if (len(motivos) > 0):
        print("Motivos: ")
        for motivo in motivos:
            print(f" - {motivo}")
    print("\n")

def obter_servicos(lista):
    """
    :param lista: recebe uma lista de serviços.
    :return: devolve a lista de serviços considerados suspeitos.
    """
    for servico in lista:
        print("------------------------------------------------------------")
        print(f"Serviço                : {servico.get('nome')}")
        print(f"Nome exibido           : {servico.get('exibido')}")
        print(f"Estado do serviço      : {servico.get('estado')}")
        print(f"Caminho                : {servico.get('caminho')}")
        print(f"Estado da assinatura   : {servico.get('assinatura')}")
        print(f"Hash                   : {servico.get('hash')}")
        print("------------------------------------------------------------")