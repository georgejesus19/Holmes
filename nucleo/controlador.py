import os
import psutil
import winreg
import shlex
from modulos import interface
from modulos import logs
from uteis import normalizar_caminho
from uteis import obter_hash
from uteis import variaveis_de_ambiente
from uteis import carregar_lista
from uteis import verificar_assinatura_digital

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
            processos.append(temporario.copy()) # porque que atribuo uma cópia ?
    item = selecionar_valor(processos)

    os.system("cls")

    resultado_assinatura = verificar_assinatura_digital.verificar_assinatura(item['caminho'])
    assinatura = "Válida" if resultado_assinatura == "Signature verified." else resultado_assinatura
    hash_processo = obter_camainho_binario(item['caminho'])

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
    pass

def analisar_servico():
    pass

def analisar_conexao_rede():
    pass

# =========================
# CONSULTA NA API VIRUSTOTAL
# =========================

def consultar_API():
    pass

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