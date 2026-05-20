import os
from modulos import processos
from modulos import persistencia_arquivos
from modulos import redes
from modulos import interface
from modulos import logs
from scripts import criar_pasta_db
from modo_manual import controlador

reload = False

if (not reload):
    os.system("cls")

criar_pasta_db.criar_ficheiro_db()
logs.criar_tabelas()
interface.menu_inicial()

os.system("cls")

while True:
    opc = interface.menu()
    match(opc):
        case 1:
            processos.obter_processos()
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 2:
            persistencia_arquivos.obter_HKCU()
        case 3:
            persistencia_arquivos.obter_HKLM()
        case 4:
            persistencia_arquivos.listar_tarefas_agendadas()
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 5:
            persistencia_arquivos.verificar_servicos_ativos()
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 6:
            persistencia_arquivos.monitorar_pasta_startup()
        case 7:
            redes.verificar_conexoes_de_rede()
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 8:
            controlador.modo_manual()
            os.system("cls")
        case 9:
            print("Obrigado por utilizar o Holmes!!!")
            break