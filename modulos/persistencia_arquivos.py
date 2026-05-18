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
from uteis import criar_string
from uteis import calcular_score
from uteis import atribuir_risco


# =========================
# FUNÇÕES AUXILIARES.
# =========================

def processar_caminho(caminho, tipos_assinatura, dados):
    caminho = os.path.expandvars(caminho.strip('"').strip())

    resultado = logs.consultar_binario(caminho)
    if resultado:
        return {
            'tarefa_executada': resultado['caminho'],
            'hash': resultado['hash'],
            'assinatura_digital': resultado['assinatura_digital'],
            'status': resultado['status']
        }

    assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)

    dados['tarefa_executada'] = caminho
    dados['hash'] = obter_hash.obter_hash(caminho)
    dados['status'] = assinatura
    dados['assinatura_digital'] = tipos_assinatura.get(
        assinatura,
        "Assinatura digital desconhecida"
    )

    logs.inserir_binario(
        dados['tarefa_executada'],
        dados['hash'],
        dados['assinatura_digital'],
        dados['status']
    )

    return dados

def tipo_caminho(caminho):
    """
    Determina o tipo de ficheiro com base no caminho fornecido, distinguindo entre executáveis normais,
    aplicações da Microsoft Store (WindowsApps) e caminhos inválidos, permitindo aplicar o tratamento adequado.

    :param caminho: Caminho do executável
    :return: Devolve o tipo de caminho
    """
    caminho = caminho.lower()

    if not os.path.exists(caminho):
        return "invalido"

    if not caminho.endswith(".exe"):
        return "nao_exe"

    if "windowsapps" in caminho:
        return "store"

    return "normal"

def analisar_normal(temp, tipos_assinatura):
    assinatura = verificar_assinatura_digital.verificar_assinatura(temp['caminho'])
    temp['hash'] = obter_hash.obter_hash(temp["caminho"])
    temp['assinatura_digital'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")
    temp['status'] = assinatura
    return temp

def tratar_store(temp):
    temp['hash'] = "Não aplicável (Microsoft Store App)"
    temp['assinatura_digital'] = "Não aplicável (Microsoft Store App)"
    temp['status'] = "StoreApp"
    return temp

def tratar_invalido(temp, tipos_assinatura):
    assinatura = verificar_assinatura_digital.verificar_assinatura(temp['caminho'])
    temp['hash'] = obter_hash.obter_hash(temp["caminho"])
    temp['assinatura_digital'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")
    temp['status'] = assinatura
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

def verificar_dados_caminho_chave_registo(valor, tipos_assinatura):
    dados = {'caminho': '', 'hash': '', 'assinatura_digital': '', 'status': ''}

    argumento = shlex.split(valor, posix=True)
    if ("\\" in argumento[0]):
        dados['caminho'] = os.path.expandvars(argumento[0])
    else:
        dados['caminho'] = os.path.expandvars(valor)

    resultado = logs.consultar_binario(dados['caminho'])

    if resultado:
        return resultado

    tipo = tipo_caminho(dados['caminho'])

    if (tipo == "normal"):
        dados = analisar_normal(dados.copy(), tipos_assinatura)
    elif (tipo == "store"):
        dados = tratar_store(dados.copy())
    else:
        dados = tratar_invalido(dados.copy(), tipos_assinatura)

    logs.inserir_binario(dados['caminho'], dados['hash'], dados['assinatura_digital'], dados['status'])

    return dados

def verificar_dados_caminho_tarefas_agendadas(valor, tipos_assinatura):

    dados = {'tarefa_executada': '','hash': '','assinatura_digital': '','status': ''}

    if ".exe" in valor.lower():
        m = re.match(r'[\S ]+\.exe[ "]', valor)
        if m:
            return processar_caminho(m.group(0), tipos_assinatura, dados)
        return processar_caminho(valor, tipos_assinatura, dados)

    if valor == "COM handler":
        dados['tarefa_executada'] = valor
        dados['assinatura_digital'] = "Válida"
        dados['hash'] = "N/A"
        dados['status'] = "N/A"
        logs.inserir_binario(dados['tarefa_executada'], dados['hash'],
                             dados['assinatura_digital'], dados['status'])
        return dados

    argumentos = shlex.split(valor, posix=False)
    if argumentos:
        caminho = argumentos[0].strip('"')
        return processar_caminho(caminho, tipos_assinatura, dados)

    return dados

def verificar_dados_servicos(caminho, tipos_assinatura):

    dados = {'caminho': caminho,'hash': '', 'assinatura_digital': '', 'status': ''}

    resultado = logs.consultar_binario(caminho)

    if resultado:
        return resultado

    assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)

    dados['hash'] = obter_hash.obter_hash(caminho)
    dados['status'] = assinatura
    dados['assinatura_digital'] = tipos_assinatura.get(assinatura, "Assinatura digital desconhecida")

    logs.inserir_binario(caminho, dados['hash'], dados['assinatura_digital'], dados['status'])

    return dados

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
    programas = list()
    temp = dict()
    tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                        'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                        'UnknownError': 'Erro na verificação da assinatura digital'}

    lista = carregar_lista.carregar_lista("listas/blacklist.txt")

    try:
        hive_nome = 'HKCU (HKEY_CURRENT_USER)' if hive == winreg.HKEY_CURRENT_USER else 'HKLM (HKEY_LOCAL_MACHINE)'
        chave = winreg.OpenKey(hive, caminho)
        temp['HK'] = hive_nome
        i = 0
        while True:
            try:
                nome, valor, tipo = winreg.EnumValue(chave, i)
                resultado_consulta = verificar_dados_caminho_chave_registo(valor, tipos_assinatura)
                temp['nome'] = nome + '.exe'
                temp['caminho'] = resultado_consulta['caminho']
                temp['tipo'] = tipo
                temp['assinatura'] = resultado_consulta['assinatura_digital']
                temp['hash'] = resultado_consulta['hash']
                temp['status'] = resultado_consulta['status']
                temp['pontuacao'] = 0
                temp['risco'] = ''

                item = calcular_score_programas_chave_registo(temp.copy(), lista)

                temp['pontuacao'] = item[0]['pontuacao']
                temp['risco'] = item[0]['risco']
                motivo = criar_string.criar_string_motivo(item[1])
                programas_copia = temp.copy()
                programas.append(programas_copia)
                mostrar_programas_chave_registo([programas_copia], item[1])

                id_binario = logs.consultar_binario(temp['caminho'])
                logs.inserir_programas_chave_registo(temp['nome'], temp['tipo'], temp['HK'], temp['pontuacao'], temp['risco'], motivo ,id_binario["id"])

                i += 1
            except OSError:
                break
        winreg.CloseKey(chave)
    except FileNotFoundError:
        print(f"Chave não encontrada: {caminho}")
    except PermissionError:
        print(f"Acesso negado à chave: {caminho}")


def calcular_score_programas_chave_registo(programa, ficheiro):
    """
    :param programa: representa o programa que está a ser analisado.
    :param ficheiro: blacklist utilizada para comparação.
    :return:
    """

    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    caminho_programa = normalizar_caminho.normalizar(programa['caminho'])

    score, motivo = pontos_assinatura.pontos_assinatura(programa['status'])
    dados_score['pontuacao'] += score

    if (programa['status'] not in ["Valid", "StoreApp"]):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_programa)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    score_local, motivos_locais = calcular_score.calcular_score_auxiliar(ficheiro, programa['nome'], caminho_programa)

    dados_score['pontuacao'] += score_local['pontuacao']
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

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
    tarefas = []
    vistos = set()
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
                        resultado_consulta = verificar_dados_caminho_tarefas_agendadas(valor, tipos_assinatura)
                        dados['tarefa_executada'] = resultado_consulta['tarefa_executada']
                        dados['assinatura'] = resultado_consulta['assinatura_digital']
                        dados['hash'] = resultado_consulta['hash']
                        dados['status'] = resultado_consulta['status']
                    elif chave in ["run as user", "executar como usuário"]:
                        dados["utilizador"] = valor

            dados['pontuacao'] = 0
            dados['risco'] = ''
            motivo = ''
            if "tarefa_executada" in dados:
                item = calcular_score_tarefas_agendadas(dados.copy(), lista)
                dados['pontuacao'] = item[0]['pontuacao']
                dados['risco'] = item[0]['risco']
                motivo = criar_string.criar_string_motivo(item[1])

            if "nome" in dados:
                nome = dados.get("nome", "").strip().lower()
                execucao = dados.get("tarefa_executada", "").strip().lower()

                task_id = f"{nome}|{execucao}"

                if task_id not in vistos:
                    vistos.add(task_id)
                    tarefas.append(dados.copy())
                    obter_tarefas_agendadas([dados.copy()], item[1])
                    id_binario = logs.consultar_binario(dados["tarefa_executada"])

                    logs.inserir_tarefas_agendadas(
                        dados["nome"],
                        dados["proxima_execucao"],
                        dados["ultima_execucao"],
                        dados["utilizador"],
                        dados["pontuacao"],
                        dados["risco"],
                        motivo,
                        id_binario["id"])

    except FileNotFoundError:
        print("ERRO: O comando 'schtasks' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")

def calcular_score_tarefas_agendadas(tarefa, ficheiro):
    """
    :param lista_tarefas: Lista de tarefas agendadas (retorno da função anterior).
    :param ficheiro: A blackklist utilizada como parâmetro de comparação.
    :return: Função de duplo retorno, devolve um dicionário com o nível de risco e a pontuação de risco
    de uma determinada tarefa agendada
    """
    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    valor_tarefa = tarefa['tarefa_executada']
    caminho_tarefa = normalizar_caminho.normalizar(valor_tarefa)

    score, motivo = pontos_assinatura.pontos_assinatura(tarefa['status'])
    dados_score['pontuacao'] += score
    if (tarefa['status'] not in ["Valid", "N/A"]):
        motivos.append(motivo)

    if (caminho_raiz.verificar_caminho_raiz(caminho_tarefa)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    score_local, motivos_locais = calcular_score.calcular_score_auxiliar(ficheiro, tarefa['nome'], caminho_tarefa)

    dados_score['pontuacao'] += score_local['pontuacao']
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos

# SERVIÇOS:
def verificar_servicos_ativos():
    """
    :return: Devolve todos os serviços ativos.
    """
    os.system("cls")
    print("Serviços em análise: \n")
    servicos = []  # lista de servicos ativos.
    assinatura = ""
    tipos_assinatura = {'Valid': 'Válida', 'NotSigned': 'Sem assinatura',
                        'HashMismatch': 'Ficheiro alterado', 'NotTrusted': 'Certificado inválido',
                        'UnknownError': 'Erro na verificação da assinatura digital'}

    lista = carregar_lista.carregar_lista("listas/blacklist_servicos.txt")

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
                    resultado_consulta = verificar_dados_servicos(dados['caminho'], tipos_assinatura)
                    dados["hash"] = resultado_consulta['hash']
                    dados["assinatura"] = resultado_consulta['assinatura_digital']
                    dados["status"] = resultado_consulta['status']

            item = calcular_score_servicos(lista, dados.copy())
            dados['risco'] = item[0]['risco']
            dados['pontuacao'] = item[0]['pontuacao']

            motivo = criar_string.criar_string_motivo(item[1])

            servicos_copia = dados.copy()
            if "nome" in dados:
                servicos.append(servicos_copia)
                obter_servicos([servicos_copia], item[1])

                id_binario = logs.consultar_binario(dados["caminho"])
                logs.inserir_servicos(dados["nome"], dados["exibido"], dados["estado"], dados["pontuacao"],
                                      dados["risco"], motivo, id_binario["id"])
    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")

def calcular_score_servicos(ficheiro, servico):
    """
    :param lista: corresponde a lista de serviços.
    :param ficheiro: Corresponde a blacklist de serviços maliciosos.
    :return: devolve uma dicionário com as informações dos suspeitos.
    """
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    nome_servico = servico['nome'].lower().strip()
    caminho_servico = normalizar_caminho.normalizar(servico['caminho'])

    score, motivo = pontos_assinatura.pontos_assinatura(servico['status'])
    dados_score['pontuacao'] += score
    if (servico['status'] != "Valid"):
        motivos.append(motivo)

    if ("_" in nome_servico):
        nome_servico = nome_base(servico["nome"].strip().lower())

    if (caminho_raiz.verificar_caminho_raiz(caminho_servico)):
        dados_score['pontuacao'] += 25
        motivos.append("Programa na raiz do disco")

    score_local, motivos_locais = calcular_score.calcular_score_auxiliar(ficheiro, nome_servico, caminho_servico)

    dados_score['pontuacao'] += score_local['pontuacao']
    motivos.extend(motivos_locais)

    dados_score['pontuacao'] = max(0, min(dados_score['pontuacao'], 100))
    dados_score['risco'] = atribuir_risco.definir_risco(dados_score)

    return dados_score, motivos

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
    for tarefa in lista:
        print("------------------------------------------------------------")
        print(f"Nome                    : {tarefa.get('nome')}")
        print(f"Próxima Execução        : {tarefa.get('proxima_execucao')}")
        print(f"Última Execução         : {tarefa.get('ultima_execucao')}")
        print(f"Tarefa Executada        : {tarefa.get('tarefa_executada')}")
        print(f"Utilizador              : {tarefa.get('utilizador')}")
        print(f"Estado da assinatura    : {tarefa.get('assinatura')}")
        print(f"Hash                    : {tarefa.get('hash')}")
        print(f"Pontuação de risco      : {tarefa.get('pontuacao')}")
        print(f"Nível de risco:         : {tarefa.get('risco')}")
        print("------------------------------------------------------------")
    if (len(motivos) > 0):
        print("Motivos: ")
        for motivo in motivos:
            print(f" - {motivo}")
    print("\n")

def obter_servicos(lista, motivos):
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
        print(f"Pontuação de risco     : {servico.get('pontuacao')}")
        print(f"Nível de risco         : {servico.get('risco')}")
        print("------------------------------------------------------------")
    if (len(motivos) > 0):
        print("Motivos: ")
        for motivo in motivos:
            print(f" - {motivo}")
    print("\n")