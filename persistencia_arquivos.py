import winreg
import subprocess
import os
import time
import shlex
import re

assinatura_cache = {}

def verificar_assinatura(caminho):
    if caminho in assinatura_cache:
        return assinatura_cache[caminho]
    try:
        comando = [
            "powershell",
            "-Command",
            f"(Get-AuthenticodeSignature '{caminho}').StatusMessage"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        status_message = resultado.stdout.strip()
        assinatura_cache[caminho] = status_message
        return status_message

    except (FileNotFoundError, OSError, subprocess.CalledProcessError, PermissionError) as erro:
        assinatura_cache[caminho] = f"Erro ao verificar assinatura {erro}"
        return assinatura_cache[caminho]

def verificar_caminho_raiz(caminho):
    partes = caminho.split("\\")
    if (partes[0] in ["C:", "D:", "E:"]):
        if (partes[1].endswith(".exe")):
            #Esta na raiz.
            return True
        else:
            #Esta no disco C, E ou D. Mas não na raiz.
            return False
    else:
        return False

def ler_chave_run(hive, caminho):
    """
    :param hive: arquivo de configurações do windows.
    :param caminho: caminho da chave de registo.
    :return: todos os programas configurados para arrancar mesmo após reinicialização.
    """
    programas = list() # guarda os programas todos.
    temp = dict() # dicionário temporário para guardar info dos programas.
    assinatura = ""
    try:
        # Abrir chave de registro com permissão de leitura
        hive_nome = 'HKCU (HKEY_CURRENT_USER)' if hive == winreg.HKEY_CURRENT_USER else 'HKLM (HKEY_LOCAL_MACHINE)'
        chave = winreg.OpenKey(hive, caminho)
        temp['HK'] = hive_nome # armazena a configuração HKCU (utilizador atual) ou HKLM (sistema)
        i = 0
        while True:
            try:
                nome, valor, tipo = winreg.EnumValue(chave, i) # lê e atribui os valores da chave de registo
                temp['nome'] = nome + '.exe'
                argumento = shlex.split(valor)
                temp['caminho'] = argumento[0]
                temp['tipo'] = tipo
                temp['assinatura'] = ''
                if (os.path.exists(argumento[0]) and argumento[0].lower().endswith('.exe')):
                    assinatura = verificar_assinatura(argumento[0])
                    if (assinatura == "Signature verified."):
                        temp['assinatura'] = 'Válida'
                    else:
                        temp['assinatura'] = assinatura
                else:
                    temp['assinatura'] = "Caminho inválido ou não encontrado"
                programas.append(temp.copy())
                i += 1
            except OSError:
                break  # Sem mais entradas
        winreg.CloseKey(chave) # fecha a chave de registo.
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

    try:
        with open(ficheiro, 'r') as blacklist:
            for linha in blacklist:
                valor_programa = linha.strip().lower()

                for programa in lista:
                    if (programa['assinatura'] == "Válida"):
                        continue

                    exec_programa = programa['nome'].lower().strip()
                    caminho_programa = programa['caminho'].lower().strip()
                    if (exec_programa == valor_programa or caminho_programa.startswith(valor_programa)):
                        if (programa['caminho'] not in controlo):
                            suspeitos.append({'nome':programa['nome'],
                                              'caminho':programa['caminho'],
                                              'tipo':programa['tipo'],
                                              'HK':responsavel,
                                              'assinatura':programa['assinatura']})
                            controlo.add(programa['caminho'].strip().lower())

        return suspeitos if (len(suspeitos) > 0) else f'Não existem programas suspeitos, iniciados por {responsavel}'
    except (FileNotFoundError, IOError, NameError) as erro:
        print(f'Erro na abertura do ficheiro: {erro}')
        return []

def listar_tarefas_agendadas():
    """
    :return: Devolve todas as tarefas agendadas no windows.
    """
    tarefas = [] # lista de tarefas agendadas
    caminho_exe = ""
    estado_assinatura = ""
    try:
        resultado = subprocess.run(["schtasks", "/query", "/fo", "LIST", "/v"],
                                   capture_output=True,
                                   text=True,
                                   encoding="mbcs",
                                   check=True)
        blocos = resultado.stdout.strip().split('\n\n')

        for bloco in blocos:
            linhas = bloco.strip().splitlines()
            dados = {}
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
                        if "\\" in valor or "/" in valor:
                            m = re.match(r'[\S ]+\.exe[ "]', valor)
                            if m:
                                m = re.match(r'[\S ]+\.exe[ "]', valor)
                                caminho_exe = os.path.expandvars(m.group(0).strip('"').strip())
                                estado_assinatura = verificar_assinatura(caminho_exe)
                                dados['tarefa_executada'] = caminho_exe
                                if (estado_assinatura == "Signature verified."):
                                    dados['assinatura'] = "Válida"
                                else:
                                    dados['assinatura'] = estado_assinatura
                            else:
                                caminho_exe = os.path.expandvars(valor)
                                estado_assinatura = verificar_assinatura(caminho_exe)
                                dados['tarefa_executada'] = caminho_exe
                                if (estado_assinatura == "Signature verified."):
                                    dados['assinatura'] = "Válida"
                                else:
                                    dados['assinatura'] = estado_assinatura
                        else:
                            if (valor == "COM handler"):
                                dados['tarefa_executada'] = valor
                                dados['assinatura'] = "Válida"
                            else:
                                bruto = valor
                                argumentos = shlex.split(bruto, posix=False)
                                if argumentos:
                                    caminho = argumentos[0].strip('"')
                                    caminho = os.path.expandvars(caminho)
                                    estado_assinatura = verificar_assinatura(caminho)
                                    dados['tarefa_executada'] = caminho
                                    if (estado_assinatura == "Signature verified."):
                                        dados['assinatura'] = "Válida"
                                    else:
                                        dados['assinatura'] = estado_assinatura
                    elif chave in ["run as user", "executar como usuário"]:
                        dados["utilizador"] = valor
            if ("nome") in dados:
                tarefas.append(dados)
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

    try:
        with open(ficheiro, 'r') as blacklist:
            for linha in blacklist:
                exec_blacklist = linha.strip().lower()

                for tarefa in lista_tarefas:
                    valor_tarefa = tarefa['tarefa_executada'].lower().strip()

                    if(tarefa['assinatura'] == "Válida"):
                        continue

                    nome_tarefa = os.path.basename(valor_tarefa)
                    caminho_tarefa = valor_tarefa
                    # Comparação
                    if (exec_blacklist == nome_tarefa or caminho_tarefa.startswith(exec_blacklist)):
                        if tarefa['tarefa_executada'] not in controlo:
                            suspeitos.append({
                                'nome': tarefa['nome'],
                                'tarefa_executada': tarefa['tarefa_executada'],
                                'proxima_execucao': tarefa['proxima_execucao'],
                                'ultima_execucao': tarefa['ultima_execucao'],
                                'utilizador': tarefa['utilizador'],
                                'assinatura': tarefa["assinatura"]
                            })
                            controlo.add(tarefa['tarefa_executada'])
        return suspeitos

    except (FileNotFoundError, IOError, NameError) as erro:
        print(f'Erro na abertura do ficheiro: {erro}')
        return []

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
                        caminho = valor
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
    servicos = [] # lista de servicos ativos.
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
                    valor =  valor.strip()
                    if chave in ["service_name", "nome_servico"]:
                        dados["nome"] = valor
                        dados["caminho"] = caminho_servico(valor)
                    elif chave in ["display_name", "nome_exibido"]:
                        dados["exibido"] = valor
                    elif chave in ["state", "estado"]:
                        dados["estado"] = valor
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
    suspeitos = []
    caminhos = set()

    try:
        with open(ficheiro, "r", encoding="utf-8") as blacklist:
            for linha in blacklist:
                exec_servico = linha.strip().lower()
                for servico in lista:
                    caminho_servico = servico["caminho"].strip().lower()
                    nome_servico = servico["nome"].strip().lower()

                    if ("_" in nome_servico):
                        nome_servico = nome_base(servico["nome"].strip().lower())

                    if ((nome_servico == exec_servico) or (verificar_caminho_raiz(caminho_servico)) or
                        (caminho_servico.startswith(exec_servico) and verificar_caminho_raiz(caminho_servico))):
                        if (servico["caminho"] not in caminhos):
                            suspeitos.append({
                                "nome": servico["nome"],
                                "caminho": servico["caminho"],
                                "exibido": servico["exibido"],
                                "estado": servico["estado"]
                            })
                            caminhos.add(servico["caminho"])
        return suspeitos
    except (FileNotFoundError, IOError) as erro:
        print(f'Erro na abertura do ficheiro: {erro}')
        return []

def monitorar_pasta_startup(quantidade=2 , tempo=5):
    """
    :param quantidade: define a quantidade de vezes que a varredura sera feita a pasta.
    :param tempo: Tempo pedido para monitoramento da pasta (em segundos) [é um parâmetro opcional].
    :return: devolve a lista das coisas adicionadas ou removidas.
    """
    startup_caminho = os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup")
    ficheiros_anteriores = set(os.listdir(startup_caminho))

    adicionados = []
    removidos = []
    i = 0

    print("Iniciando o monitoramento da pasta Startup:")
    try:
        while (i < quantidade):
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
                print("Nenhuma alteração detectada.")
            ficheiros_anteriores = ficheiros_atuais
            i += 1
        return adicionados, removidos
    except KeyboardInterrupt:
        print("Monitoramento encerrado")
def obter_tarefas_agendadas(lista, texto="Tarefas Agendadas: "):
    """
    :param lista: lista das tarefas agendadas.
    :param texto:
    :return: todas as tarefas agendadas ou consideradas suspeitas.
    """
    print(texto)
    for linha in lista:
        print(f"Nome: {linha.get('nome')}")
        print(f"Próxima Execução: {linha.get('proxima_execucao')}")
        print(f"Última Execução: {linha.get('ultima_execucao')}")
        print(f"Tarefa Executada: {linha.get('tarefa_executada')}")
        print(f"Utilizador: {linha.get('utilizador')}")
        print(f"Estado da assinatura: {linha.get('assinatura')}")
        print("---")

def obter_programas(lista):
    """
    :param lista: recebe a lista dos programas
    :return: devlolve os programas suspeitos (na chave de registo)
    """
    if isinstance(lista, list):
        for programa in lista:
            print(f'Nome: {programa['nome']}\nCaminho: {programa['caminho']}\nTipo: {programa['tipo']}\nIniciado por: {programa['HK']}\nEstado da assinatura: {programa['assinatura']}')
            print("-----------------------------------------------------------------------------------------------")
    else:
        print(f'{lista}')

def obter_servicos(lista, mensagem):
    """
    :param lista: recebe uma lista de serviços.
    :return: devolve a lista de serviços considerados suspeitos.
    """
    tamanho = len(lista)
    if (tamanho > 0):
        print(mensagem)
        for servico in lista:
            print(f"Servico: {servico['nome']}\nNome exibido: {servico['exibido']}\nEstado: {servico['estado']}\nCaminho: {servico['caminho']}")
            print("-----------------------------------------------------------------------------------------------")
    else:
        print("Não foram detectados serviços maliciosos")
    input("Pressione enter para voltar ao menu inicial...")
    os.system("cls")

def obter_HKCU():
    utilizador = ler_chave_run(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
    obter_programas(utilizador)

def obter_HKLM():
    maquina = ler_chave_run(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    obter_programas(maquina)

def obter_suspeitos_HKCU(ficheiro, responsavel):
    utilizador = ler_chave_run(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
    HKCU = programas_suspeitos(utilizador, ficheiro,responsavel)
    obter_programas(HKCU)

def obter_suspeitos_HKLM(ficheiro, responsavel):
    maquina = ler_chave_run(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
    HKLM = programas_suspeitos(maquina, ficheiro,responsavel)
    obter_programas(HKLM)



#Testado
#utilizador = ler_chave_run(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run")
#maquina = ler_chave_run(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run")
#HKCU = programas_suspeitos(utilizador, '../listas/blacklist.txt', 'HKCU (HKEY_CURRENT_USER)')
#HKLM = programas_suspeitos(maquina, '../listas/blacklist.txt', 'HKLM (HKEY_LOCAL_MACHINE)')

#print("Programas configurados nas chaves de registo")
#obter_programas(utilizador)
#obter_programas(maquina)
#print("-=" * 35)

#tarefas = tarefas_suspeitas(listar_tarefas_agendadas(), "../listas/blacklist.txt")
#print("-=" * 35)
#obter_tarefas_agendadas(tarefas, "Tarefas Suspeitas")

#print("-=" * 35)
#print("Serviços ativos")
#servicos = verificar_servicos_ativos()
#obter_servicos(servicos)
#obter_servicos(verificar_servicos_suspeitos("../listas/blacklist_servicos.txt", servicos))
#print("-=" * 35)

#lista1 , lista2 = monitorar_pasta_startup()
#print(lista1, lista2)
#print("-=" * 35)










