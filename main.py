import os
from uteis import carregar_lista
from modulos import processos
from modulos import persistencia_arquivos
from modulos import redes
from modulos import interface

blacklist = carregar_lista.carregar_lista("listas/blacklist.txt")
blacklist_servicos = carregar_lista.carregar_lista("listas/blacklist_servicos.txt")
ips_suspeitos = carregar_lista.carregar_lista("listas/ips_suspeitos.txt")
dominios_suspeitos = carregar_lista.carregar_lista("listas/dominios_suspeitos.txt")

reload = False

if (not reload):
    os.system("cls")

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
            p = processos.obter_processos(False)
            processos.obter_processos_suspeitos(blacklist, p)
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 3:
            persistencia_arquivos.obter_HKCU()
        case 4:
            persistencia_arquivos.obter_HKLM()
        case 5:
            persistencia_arquivos.obter_suspeitos_HKCU(blacklist, "HKCU (HKEY_CURRENT_USER)")
            input("Pression enter para voltar ao menu inicial...")
            os.system("cls")
        case 6:
            persistencia_arquivos.obter_suspeitos_HKLM(blacklist, "HKLM (HKEY_LOCAL_MACHINE)")
            input("Pression enter para voltar ao menu inicial...")
            os.system("cls")
        case 7:
            persistencia_arquivos.listar_tarefas_agendadas()
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 8:
            tarefas = persistencia_arquivos.listar_tarefas_agendadas(False)
            persistencia_arquivos.tarefas_suspeitas(tarefas, blacklist)
            input("Pressione enter para voltar ao menu inicial...")
            os.system("cls")
        case 9:
            servicos = persistencia_arquivos.verificar_servicos_ativos()
            persistencia_arquivos.obter_servicos(servicos,"Lista de serviços do windows: ")
        case 10:
            servicos = persistencia_arquivos.verificar_servicos_ativos()
            servicos_suspeitos = persistencia_arquivos.verificar_servicos_suspeitos(blacklist_servicos, servicos)
            persistencia_arquivos.obter_servicos(servicos_suspeitos, "Lista de serviços suspeitos: ")
        case 11:
            persistencia_arquivos.monitorar_pasta_startup()
        case 12:
            conexoes = redes.verificar_conexoes_de_rede()
            redes.mostrar_conexoes(conexoes)
        case 13:
            conexoes = redes.verificar_conexoes_de_rede()
            conexoes_suspeitas = redes.verificar_conexoes_suspeitas(conexoes, ips_suspeitos, dominios_suspeitos)
            redes.mostrar_conexoes(conexoes_suspeitas, "Conexões Suspeitas:\n")
        case 14:
            print("Obrigado por utilizar o Holmes!!!")
            break