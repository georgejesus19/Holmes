import winreg
import subprocess
import os
import time
import shlex
import re
from modulos import logs
from pathlib import Path
from uteis import obter_hash
from uteis import verificar_assinatura_digital
from uteis import variaveis_de_ambiente
from uteis import normalizar_caminho
from uteis import validar_resposta


def verificar_caminho_raiz(caminho):
    p = Path(caminho)
    # parent como string e normalize para barras
    parent_str = str(p.parent).replace("/", "\\")
    return (p.suffix.lower() == ".exe" and parent_str == p.anchor)


def ler_chave_run(hive, caminho, mostrar=True):
    """
    :param hive: arquivo de configurações do windows.
    :param caminho: caminho da chave de registo.
    :return: todos os programas configurados para arrancar mesmo após reinicialização.
    """
    programas = list()  # guarda os programas todos.
    temp = dict()  # dicionário temporário para guardar info dos programas.
    assinatura = ""
    tabela = ""

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
                if not mostrar:
                    print(f"Programa em análise: {temp['nome']}")
                argumento = shlex.split(valor, posix=True)
                if ("\\" in argumento[0]):
                    temp['caminho'] = os.path.expandvars(argumento[0])
                else:
                    temp['caminho'] = os.path.expandvars(valor)
                temp['tipo'] = tipo
                temp['assinatura'] = ''
                temp['Hash'] = ''
                if (os.path.exists(temp['caminho']) and temp['caminho'].lower().endswith('.exe')):
                    assinatura = verificar_assinatura_digital.verificar_assinatura(temp['caminho'])
                    temp['Hash'] = obter_hash.obter_hash(temp["caminho"])
                    if (assinatura == "Signature verified."):
                        temp['assinatura'] = 'Válida'
                    else:
                        temp['assinatura'] = assinatura
                else:
                    temp['assinatura'] = "Caminho inválido ou não encontrado"
                    temp['Hash'] = "Caminho inválido ou não encontrado (não foi possível obter o hash)"
                logs.inserir_programas_chave_registo(temp['nome'], temp['caminho'],
                                                     temp['tipo'],temp['HK'],
                                                     temp['assinatura'], temp['Hash'], tabela)
                programas.append(temp.copy())
                if mostrar:
                    obter_programas([temp.copy()])
                i += 1
            except OSError:
                break  # Sem mais entradas
        winreg.CloseKey(chave)  # fecha a chave de registo.
        return programas

    except FileNotFoundError:
        print(f"Chave não encontrada: {caminho}")
        return []
    except PermissionError:
        print(f"Acesso negado à chave: {caminho}")
        return []


def programas_suspeitos(lista, ficheiro, responsavel):
    """
    :param lista: lista de programas numa chave de registo (normalmente lista de dicionários).
    :param ficheiro: blacklist utilizada para comparação.
    :param responsavel: HKCU (utilizador atual) ou HKLM (sistema)
    :return:
    """
    suspeitos = []
    controlo = set()
    tabela = "programas_HKCU_suspeitos" if responsavel == "HKCU (HKEY_CURRENT_USER)" else "programas_HKLM_suspeitos"

    for programa in lista:
        if (programa['assinatura'] == "Válida"):
            continue

        exec_programa = programa['nome'].lower().strip()
        caminho_programa = normalizar_caminho.normalizar(programa['caminho'])

        for valor_programa in ficheiro:
            if (exec_programa == valor_programa) or \
               (caminho_programa.startswith(variaveis_de_ambiente.expandir_caminhos(valor_programa))):
                if (caminho_programa not in controlo):
                    suspeitos.append({'nome': programa['nome'],
                                      'caminho': programa['caminho'],
                                      'tipo': programa['tipo'],
                                      'HK': responsavel,
                                      'assinatura': programa['assinatura'],
                                      'Hash': programa['Hash']})
                    logs.inserir_programas_chave_registo(programa['nome'], programa['caminho'],
                                                         programa['tipo'], programa['HK'],
                                                         programa['assinatura'], programa['Hash'],
                                                         tabela)
                    controlo.add(caminho_programa)
    os.system("cls")
    tamanho = len(suspeitos)
    if (tamanho > 0):
        print(responsavel)
        print("Programas suspeitos detetados!")
        resposta = validar_resposta.validar_resposta()
        if (resposta in ["SIM", "S"]):
            logs.consultar_programas(tabela)
    else:
        print("Não existem programas suspeitos na chave de registo")

def listar_tarefas_agendadas(mostrar=True):
    """
    :return: Devolve todas as tarefas agendadas no windows.
    """
    os.system("cls")
    tarefas = []  # lista de tarefas agendadas
    tarefas_vistas = set()
    caminho_exe = ""
    estado_assinatura = ""

    print("Tarefas em análise: \n")
    try:
        resultado = subprocess.run(["schtasks", "/query", "/fo", "LIST", "/v"],
                                   capture_output=True,
                                   text=True,
                                   encoding="mbcs",
                                   check=True)
        blocos = re.split(r'\n(?=TaskName:)', resultado.stdout)
        for bloco in blocos:
            linhas = bloco.strip().splitlines()
            if not mostrar:
                if linhas:  # garante que o bloco não está vazio
                    # Pega o nome da tarefa da primeira linha do bloco
                    primeira_linha = linhas[0]
                    if primeira_linha.lower().startswith("taskname:"):
                        nome_tarefa = primeira_linha.split(":", 1)[1].strip()
                        print(f"Em análise: {nome_tarefa}")  # print em tempo real
            dados = {}
            for linha in linhas:
                if ":" in linha:
                    chave, valor = linha.split(":", 1)
                    chave = chave.strip().lower()
                    valor = valor.strip()
                    if chave in ["taskname", "nome da tarefa"]:
                        dados["nome"] = valor
                        #print(f"Em analise: {dados["nome"]}")
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
                                estado_assinatura = verificar_assinatura_digital.verificar_assinatura(caminho_exe)
                                dados['hash'] = obter_hash.obter_hash(caminho_exe)
                                dados['tarefa_executada'] = caminho_exe
                                if (estado_assinatura == "Signature verified."):
                                    dados['assinatura'] = "Válida"
                                else:
                                    dados['assinatura'] = estado_assinatura
                            else:
                                caminho_exe = os.path.expandvars(valor)
                                estado_assinatura = verificar_assinatura_digital.verificar_assinatura(caminho_exe)
                                dados['hash'] = obter_hash.obter_hash(caminho_exe)
                                dados['tarefa_executada'] = caminho_exe
                                if (estado_assinatura == "Signature verified."):
                                    dados['assinatura'] = "Válida"
                                else:
                                    dados['assinatura'] = estado_assinatura
                        else:
                            if (valor == "COM handler"):
                                dados['tarefa_executada'] = valor
                                dados['assinatura'] = "Válida"
                                dados['hash'] = "N/A"
                            else:
                                bruto = valor
                                argumentos = shlex.split(bruto, posix=False)
                                if argumentos:
                                    caminho = argumentos[0].strip('"')
                                    caminho = os.path.expandvars(caminho)
                                    estado_assinatura = verificar_assinatura_digital.verificar_assinatura(caminho)
                                    dados['tarefa_executada'] = caminho
                                    dados['hash'] = obter_hash.obter_hash(caminho)
                                    if (estado_assinatura == "Signature verified."):
                                        dados['assinatura'] = "Válida"
                                    else:
                                        dados['assinatura'] = estado_assinatura
                    elif chave in ["run as user", "executar como usuário"]:
                        dados["utilizador"] = valor
            if ("nome") in dados:
                tarefas.append(dados.copy())
                logs.inserir_tarefas_agendadas(dados['nome'], dados['proxima_execucao'],
                                               dados['ultima_execucao'], dados['tarefa_executada'],
                                               dados['utilizador'], dados['hash'],
                                               dados['assinatura'], "tarefas_agendadas")
            if mostrar:
                obter_tarefas_agendadas([dados.copy()])

    except FileNotFoundError:
        print("ERRO: O comando 'schtasks' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")
    return tarefas

def tarefas_suspeitas(lista_tarefas, ficheiro):
    """
    :param lista_tarefas: Lista de tarefas agendadas (retorno da função anterior).
    :param ficheiro: A blackklist utilizada como parâmetro de comparação.
    :return: devolve uma lista com as tarefas consideradas suspeitas.
    """
    suspeitos = []
    controlo = set()

    for tarefa in lista_tarefas:
        valor_tarefa = tarefa['tarefa_executada']

        if (tarefa['assinatura'] == "Válida"):
            continue

        nome_tarefa = os.path.basename(valor_tarefa)
        caminho_tarefa = normalizar_caminho.normalizar(valor_tarefa)

        for exec_blacklist in ficheiro:
            # Comparação
            if (exec_blacklist == nome_tarefa or \
               (caminho_tarefa.startswith(variaveis_de_ambiente.expandir_caminhos(exec_blacklist)))):
                if tarefa['tarefa_executada'] not in controlo:
                    suspeitos.append({
                        'nome': tarefa['nome'],
                        'tarefa_executada': tarefa['tarefa_executada'],
                        'proxima_execucao': tarefa['proxima_execucao'],
                        'ultima_execucao': tarefa['ultima_execucao'],
                        'utilizador': tarefa['utilizador'],
                        'assinatura': tarefa["assinatura"],
                        'hash': tarefa['hash']
                    })
                    logs.inserir_tarefas_agendadas(tarefa['nome'], tarefa['proxima_execucao'],
                                                   tarefa['ultima_execucao'], tarefa['tarefa_executada'],
                                                   tarefa['utilizador'], tarefa['hash'],
                                                   tarefa['assinatura'], "tarefas_agendadas_suspeitas")
                    controlo.add(tarefa['tarefa_executada'])
    os.system("cls")
    tamanho = len(suspeitos)
    if (tamanho > 0):
        print("Tarefas Suspeitas detetadas:")
        resposta = validar_resposta.validar_resposta()
        if (resposta in ["SIM", "S"]):
            logs.consultar_tarefas_agendadas("tarefas_agendadas_suspeitas")
    else:
        print("Não existem tarefas agendadas suspeitas\n")


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


def verificar_servicos_ativos():
    """
    :return: Devolve todos os serviços ativos.
    """
    os.system("cls")
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
                servicos.append(dados)
        return servicos
    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")


def nome_base(servico):
    """
    :param servico: nome do serviço em questão
    :return: devolce o servico (ignorando o identificador [vem depois do "_"]
    """
    return servico.split("_")[0].strip().lower()


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
                    caminhos.add(caminho_servico)
    return suspeitos

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


def obter_tarefas_agendadas(lista):
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
        print("------------------------------------------------------------")


def obter_programas(lista):
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
            print(f"Hash                   : {programa.get('Hash')}")
            print("------------------------------------------------------------")


def obter_servicos(lista, mensagem):
    """
    :param lista: recebe uma lista de serviços.
    :return: devolve a lista de serviços considerados suspeitos.
    """
    os.system("cls")
    tamanho = len(lista)
    if (tamanho > 0):
        print(mensagem)
        for servico in lista:
            print("------------------------------------------------------------")
            print(f"Serviço                : {servico.get('nome')}")
            print(f"Nome exibido           : {servico.get('exibido')}")
            print(f"Estado do serviço      : {servico.get('estado')}")
            print(f"Caminho                : {servico.get('caminho')}")
            print(f"Estado da assinatura   : {servico.get('assinatura')}")
            print(f"Hash                   : {servico.get('hash')}")
            print("------------------------------------------------------------")
    else:
        print("Não foram detectados serviços maliciosos")
    input("Pressione enter para voltar ao menu inicial...")
    os.system("cls")


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


def obter_suspeitos_HKCU(ficheiro, responsavel):
    os.system("cls")
    utilizador = ler_chave_run(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", False)
    programas_suspeitos(utilizador, ficheiro, responsavel)


def obter_suspeitos_HKLM(ficheiro, responsavel):
    os.system("cls")
    maquina = ler_chave_run(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run", False)
    programas_suspeitos(maquina, ficheiro, responsavel)