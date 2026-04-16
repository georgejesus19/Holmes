import os
from modulos import interface
from modulos import logs

mensagem = "Pressione enter para voltar ao menu do modo manual..."

# =========================
# ANÁLISE PRINCIPAL
# =========================

def analisar_processo():
    pass

def analisar_programa_chave_registo():
    pass

def analisar_tarefa_agendada():
    pass

def analisar_servico():
    pass

def analisar_conexao_rede():
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
        6: mostrar_processos_db,
        7: mostrar_processos_suspeitos_db,
        8: mostrar_programas_HKCU_db,
        9: mostrar_programas_suspeitos_HKCU_db,
        10: mostrar_programas_HKLM_db,
        11: mostrar_programas_suspeitos_HKLM_db,
        12: mostrar_tarefas_agendadas_db,
        13: mostrar_tarefas_agendadas_suspeitas_db,
        14: mostrar_servicos_db,
        15: mostrar_servicos_suspeitos_db,
        16: mostrar_conexoes_db,
        17: mostrar_conexoes_suspeitas_db,
    }
    os.system("cls")
    while True:
        opc = interface.menu_modo_manual()
        os.system("cls")
        funcao = opcoes.get(opc)

        if (opc == 18):
            break

        if funcao:
            funcao()
        else:
            print("Opção inválida")