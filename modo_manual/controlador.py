import os
from modo_manual import analise_processo as a_processo
from modo_manual import analise_persistencia as a_persistencia
from modo_manual import analise_conexoes_rede as a_conexoes
from modulos import interface
from modulos import logs
from API import virusTotal

mensagem = "Pressione enter para voltar ao menu do modo manual..."

tipos_assinatura = {'Valid':'Válida', 'NotSigned':'Sem assinatura',
                    'HashMismatch':'Ficheiro alterado', 'NotTrusted':'Certificado inválido',
                    'UnknownError':'Erro na verificação da assinatura digital'}
# =========================
# FUNÇÕES AUXILIARES.
# =========================

def exibir_resultados_consulta(resultado):
    print("\n")
    os.system("cls")
    print("---------------- Resultados da consulta ----------------")
    if (isinstance (resultado, dict)):
        print(f"Número de motores que indicaram este hash pertecence a uma malware: {resultado["malicious"]}")
        print(f"Número de motores que detectaram comportamento suspeito: {resultado["suspicious"]}")
        print(f"Número de motores que indicaram que este hash pertence a um programa inofensivo: {resultado["harmless"]}")
        print(f"Número de motores que indicaram que não conhecem o hash fornecido: {resultado["undetected"]}")
    else:
        print(resultado)

# =========================
# ANÁLISE PRINCIPAL
# =========================

def analisar_processo():
    a_processo.analisar_processo(tipos_assinatura)

def analisar_programa_chave_registo_HKCU():
    a_persistencia.analisar_programa_chave_registo_HKCU(tipos_assinatura)

def analisar_programa_chave_registo_HKLM():
    a_persistencia.analisar_programa_chave_registo_HKLM(tipos_assinatura)

def analisar_tarefa_agendada():
    a_persistencia.analisar_tarefa_agendada(tipos_assinatura)

def analisar_servico():
    a_persistencia.analisar_servico(tipos_assinatura)

def analisar_conexao_rede():
    a_conexoes.analisar_conexao_rede(tipos_assinatura)

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

# =========================
# EXIBIÇÃO DE LOGS (ERROS & AÇÕES)
# =========================

def mostrar_logs_acoes():
    pass

def mostrar_logs_erros():
    pass

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
        13: mostrar_conexoes_db,
        14: mostrar_logs_acoes,
        15: mostrar_logs_erros
    }

    os.system("cls")
    while True:
        opc = interface.menu_modo_manual()
        os.system("cls")
        funcao = opcoes.get(opc)

        if (opc == 16):
            break

        if funcao:
            funcao()
            input("Pressione enter para voltar...")
            os.system("cls")
        else:
            print("Opção inválida")