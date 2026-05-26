import os
import re
import winreg
import subprocess
from acoes import servico
from acoes import chave_registo
from acoes import tarefa_agendada
from modulos import logs as l
from modulos import persistencia_arquivos as p
from uteis import normalizar_caminho
from uteis import calcular_score
from uteis import atribuir_risco
from uteis import pontos_assinatura
from uteis import caminho_raiz
from uteis import carregar_lista
from uteis import criar_string
from uteis import selecionar_valor
from uteis import validar_resposta

# =========================
# ANÁLISE PRINCIPAL (PROGRAMAS NA CHAVE DE REGISTO) & CÁLCULO DE SCORE
# =========================

def programas_chave_registo(hive, caminho, tipos_assinatura):
    os.system("cls")
    temporario = dict()
    programas = list()

    ficheiro = carregar_lista.carregar_lista("listas/blacklist.txt")

    try:
        # Abrir chave de registro com permissão de leitura
        chave = winreg.OpenKey(hive, caminho)
        temporario['HK'] = 'HKCU' if hive == winreg.HKEY_CURRENT_USER else 'HKLM'
        i = 0
        while True:
            try:
                nome, valor, tipo = winreg.EnumValue(chave, i)  # lê e atribui os valores da chave de registo
                temporario['nome'] = nome + '.exe'
                temporario['entrada'] = nome
                temporario['caminho'] = valor
                temporario['tipo'] = tipo
                programas.append(temporario.copy())
                i += 1
            except OSError:
                break  # Sem mais entradas
        winreg.CloseKey(chave)  # fecha a chave de registo.

        item = selecionar_valor.selecionar_valor(programas)

        if item == 0:
            return

        os.system("cls")

        resultado_consulta = p.verificar_dados_caminho_chave_registo(item['caminho'], tipos_assinatura)

        caminho_programa = resultado_consulta['caminho']
        status = resultado_consulta['status']
        assinatura = resultado_consulta['assinatura_digital']
        hash_programa = resultado_consulta['hash']

        info_score = calcular_score_programa_chave_registo(ficheiro, item, status, caminho_programa)

        pontuacao = info_score[0]['pontuacao']
        risco = info_score[0]['risco']
        motivos = criar_string.criar_string_motivo(info_score[1])

        print("Dados do programa")
        print("------------------------------------")
        print(f"Nome do programa: {item['nome']}")
        print(f"Caminho: {caminho_programa}")
        print(f"Tipo: {item['tipo']}")
        print(f"Iniciado por: {item['HK']}")
        print(f"Hash do programa: {hash_programa}")
        print(f"Estado da assinatura digital: {assinatura}")
        print(f"Pontuação de risco: {pontuacao}")
        print(f"Nível de risco: {risco}")
        print(f"Motivos: {motivos}")
        print("------------------------------------")

        id_binario = l.consultar_binario(caminho_programa)
        l.inserir_programas_chave_registo(item['nome'], item['tipo'], item['HK'], pontuacao, risco, motivos, id_binario["id"])

        resposta = validar_resposta.validar_resposta("Deseja remover esta entrada")

        if (resposta in ["SIM", "S"]):
            chave_registo.remover_entrada_chave_registo(item['HK'], caminho, item['entrada'])

    except FileNotFoundError:
        print(f"Chave não encontrada: {caminho}")
    except PermissionError:
        print(f"Acesso negado à chave: {caminho}")


def calcular_score_programa_chave_registo(ficheiro, programa, status, caminho):
    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    caminho_programa = normalizar_caminho.normalizar(caminho)

    score, motivo = pontos_assinatura.pontos_assinatura(status)
    dados_score['pontuacao'] += score

    if (status not in ["Valid", "StoreApp"]):
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

def analisar_programa_chave_registo_HKCU(tipos_assinatura):
    programas_chave_registo(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Run",tipos_assinatura)

def analisar_programa_chave_registo_HKLM(tipos_assinatura):
    programas_chave_registo(winreg.HKEY_LOCAL_MACHINE,r"Software\Microsoft\Windows\CurrentVersion\Run", tipos_assinatura)


# =========================
# ANÁLISE PRINCIPAL (TAREFAS AGENDADAS) & CÁLCULO DE SCORE
# =========================

def analisar_tarefa_agendada(tipos_assinatura):

    os.system("cls")
    tarefas_agendadas = list()
    vistos = set()

    ficheiro = carregar_lista.carregar_lista("listas/blacklist.txt")

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
                        dados['tarefa_executada'] = valor
                    elif chave in ["run as user", "executar como usuário"]:
                        dados["utilizador"] = valor

            if "nome" in dados:
                nome = dados.get("nome", "").strip().lower()
                execucao = dados.get("tarefa_executada", "").strip().lower()
                task_id = f"{nome}|{execucao}"
                if task_id not in vistos:
                    vistos.add(task_id)
                    tarefas_agendadas.append(dados.copy())

        item = selecionar_valor.selecionar_valor(tarefas_agendadas)

        if item == 0:
            return

        os.system("cls")

        resultado_consulta = p.verificar_dados_caminho_tarefas_agendadas(item['tarefa_executada'], tipos_assinatura)

        caminho = resultado_consulta['tarefa_executada']
        status = resultado_consulta['status']
        assinatura = resultado_consulta['assinatura_digital']
        hash = resultado_consulta['hash']

        info_score = calcular_score_tarefas_agendadas(ficheiro, item, status, caminho)

        pontuacao = info_score[0]['pontuacao']
        risco = info_score[0]['risco']
        motivos = criar_string.criar_string_motivo(info_score[1])

        print("Dados da tarefa agendada: ")
        print("-----------------------------")
        print(f"Nome: {item['nome']}")
        print(f"Última execução: {item['ultima_execucao']}")
        print(f"Proxima execução: {item['proxima_execucao']}")
        print(f"Caminho: {caminho}")
        print(f"Utilizador: {item['utilizador']}")
        print(f"Hash do executável: {hash}")
        print(f"Estado da assinatura digital: {assinatura}")
        print(f"Pontuação de risco: {pontuacao}")
        print(f"Nível de risco: {risco}")
        print(f"Motivos: {motivos}")
        print("-----------------------------")

        id_binario = l.consultar_binario(caminho)
        l.inserir_tarefas_agendadas(item['nome'], item['proxima_execucao'], item['ultima_execucao'],
                                    item['utilizador'], pontuacao, risco, motivos, id_binario["id"])

        resposta = validar_resposta.validar_resposta("Deseja desativar a tarefa agendada")

        if (resposta in ["SIM", "S"]):
            tarefa_agendada.desativar_tarefa_agendada(item['nome'])

    except FileNotFoundError:
        print("ERRO: O comando 'schtasks' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")


def calcular_score_tarefas_agendadas(ficheiro, tarefa, status, caminho):
    """
    :param lista_tarefas: Lista de tarefas agendadas (retorno da função anterior).
    :param ficheiro: A blackklist utilizada como parâmetro de comparação.
    :return: Função de duplo retorno, devolve um dicionário com o nível de risco e a pontuação de risco
    de uma determinada tarefa agendada
    """
    dados_score = {'pontuacao': 0, 'risco': ''}
    motivos = []

    caminho_tarefa = normalizar_caminho.normalizar(caminho)

    score, motivo = pontos_assinatura.pontos_assinatura(status)
    dados_score['pontuacao'] += score
    if (status not in ["Valid", "N/A"]):
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

# =========================
# ANÁLISE PRINCIPAL (SERVIÇOS) & CÁLCULO DE SCORE
# =========================

def analisar_servico(tipos_assinatura):
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

        item = selecionar_valor.selecionar_valor(servicos)

        if item == 0:
            return

        os.system("cls")

        resultado_consulta = p.verificar_dados_servicos(item['caminho'], tipos_assinatura)

        caminho = resultado_consulta['caminho']
        status = resultado_consulta['status']
        assinatura = resultado_consulta['assinatura_digital']
        hash = resultado_consulta['hash']

        info_score = calcular_score_servicos(ficheiro, item, status, caminho)

        pontuacao = info_score[0]['pontuacao']
        risco = info_score[0]['risco']
        motivos = criar_string.criar_string_motivo(info_score[1])

        print("Dados do serviço: ")
        print("-----------------------")
        print(f"Nome do serviço: {item['nome']}")
        print(f"Nome exibido: {item['exibido']}")
        print(f"Caminho: {caminho}")
        print(f"Estado do serviço: {item['estado']}")
        print(f"Hash do executável: {hash}")
        print(f"Estado da assinatura digital: {assinatura}")
        print(f"Pontuação de riscco: {pontuacao}")
        print(f"Nível de risco: {risco}")
        print(f"Motivos: {motivos}")
        print("-----------------------")

        id_binario = l.consultar_binario(caminho)
        l.inserir_servicos(item['nome'], item['exibido'], item['estado'], pontuacao, risco, motivos, id_binario["id"])

        resposta = validar_resposta.validar_resposta("Deseja desativar o serviço")

        if (resposta in ["SIM", "S"]):
            servico.desativar_servico(item['nome'])

    except FileNotFoundError:
        print("ERRO: O comando 'sc query' não foi encontrado. Verifique o PATH.")
    except PermissionError:
        print("ERRO: Permissão negada. Execute o script como administrador.")
    except subprocess.CalledProcessError as e:
        print(f"ERRO: O comando falhou (código {e.returncode}).")
    except UnicodeDecodeError:
        print("ERRO: Falha ao decodificar a saída. Tente alterar o encoding.")

def calcular_score_servicos(ficheiro, servico, status, caminho):
    """
    :param lista: corresponde a lista de serviços.
    :param ficheiro: Corresponde a blacklist de serviços maliciosos.
    :return: devolve uma dicionário com as informações dos suspeitos.
    """
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    nome_servico = servico['nome'].lower().strip()
    caminho_servico = normalizar_caminho.normalizar(caminho)

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