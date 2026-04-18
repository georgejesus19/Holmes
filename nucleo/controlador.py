import os
import psutil

from modulos import interface
from modulos import logs
from uteis import normalizar_caminho
from uteis import obter_hash
from uteis import verificar_assinatura_digital


mensagem = "Pressione enter para voltar ao menu do modo manual..."

# =========================
# FUNÇÕES COMUNS.
# =========================

def selecionar_valor(lista):
    i = 0
    for i, binario in enumerate(lista):
        print(f"{i + 1} -> Nome: {binario['nome']}")
    total = i

    while True:
        try:
            opc = int(input(f"Selecione um valor entre 1 e {total + 1}: "))
            if ((opc > total) or (opc <= 0)):
                print("Selecione uma opção válida!")
            else:
                break
        except (ValueError):
            print("Selecione uma opção válida!")
    return lista[opc - 1]

# =========================
# ANÁLISE PRINCIPAL
# =========================

def analisar_processo():
    os.system("cls")
    temporario = dict() # Irá armazenar de forma temporário dados relativos a um processo.
    processos = list() # Irá armazenar os respectivos dados vindos do dicionário temporário.
    print("Processos disponíveis para análise: \n")
    for process in psutil.process_iter(['name', 'exe']):
        try:
            caminho = process.exe()
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            caminho = "Acesso negado ou processo terminado"
        temporario['nome'] = process.name()
        temporario['caminho'] = normalizar_caminho.normalizar(caminho)
        if (temporario['nome'].endswith(".exe")):
            processos.append(temporario.copy()) # porque que atribuo uma cópia ?
    item = selecionar_valor(processos)

    os.system("cls")
    assinatura = "Válida" \
    if verificar_assinatura_digital.verificar_assinatura(item['caminho']) == "Signature verified." else \
    verificar_assinatura_digital.verificar_assinatura(item['caminho'])

    print("Dados do binário:")
    print("--------------------")
    print(f"Nome: {item['nome']}")
    print(f"Caminho: {item['caminho']}")
    print(f"Hash do executável: {obter_hash.obter_hash(item['caminho'])}")
    print(f"Estado da assinatura digital: {assinatura}")
    print("--------------------")

def analisar_programa_chave_registo():
    pass

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
        2: analisar_programa_chave_registo,
        3: analisar_tarefa_agendada,
        4: analisar_servico,
        5: analisar_conexao_rede,
        6: consultar_API,
        7: mostrar_processos_db,
        8: mostrar_processos_suspeitos_db,
        9: mostrar_programas_HKCU_db,
        10: mostrar_programas_suspeitos_HKCU_db,
        11: mostrar_programas_HKLM_db,
        12: mostrar_programas_suspeitos_HKLM_db,
        13: mostrar_tarefas_agendadas_db,
        14: mostrar_tarefas_agendadas_suspeitas_db,
        15: mostrar_servicos_db,
        16: mostrar_servicos_suspeitos_db,
        17: mostrar_conexoes_db,
        18: mostrar_conexoes_suspeitas_db,
    }

    os.system("cls")
    while True:
        opc = interface.menu_modo_manual()
        os.system("cls")
        funcao = opcoes.get(opc)

        if (opc == 19):
            break

        if funcao:
            funcao()
            input("Pressione enter para voltar...")
            os.system("cls")
        else:
            print("Opção inválida")