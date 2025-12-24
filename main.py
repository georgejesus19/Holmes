import os

from modulos import processos
from modulos import persistencia_arquivos
from modulos import interface

blacklist = "listas/blacklist.txt"
blacklist_servicos = "listas/blacklist_servicos.txt"
ips_suspeitos = "listas/ips_suspeitos.txt"

reload = False

if (not reload):
    os.system("cls")

while True:
    opc = interface.menu()
    match(opc):
        case 1:
            p = processos.obter_processos()
            processos.mostrar_processos(p)
        case 2:
            p = processos.obter_processos()
            p_s = processos.obter_processos_suspeitos(blacklist, p)
            processos.mostrar_processos(p_s)
        case 3:
            persistencia_arquivos.obter_HKCU()
        case 4:
            persistencia_arquivos.obter_HKLM()
        case 5:
            persistencia_arquivos.obter_suspeitos_HKCU(blacklist, "HKCU (HKEY_CURRENT_USER)")
        case 6:
            persistencia_arquivos.obter_suspeitos_HKLM(blacklist, "HKLM (HKEY_LOCAL_MACHINE)")
        case 7:
            tarefas = persistencia_arquivos.listar_tarefas_agendadas()
            persistencia_arquivos.obter_tarefas_agendadas(tarefas, "Tarefas agendadas")
        case 8:
            tarefas = persistencia_arquivos.listar_tarefas_agendadas()
            tarefas_suspeitas = persistencia_arquivos.tarefas_suspeitas(tarefas, blacklist)
            persistencia_arquivos.obter_tarefas_agendadas(tarefas_suspeitas, "Tarefas Suspeitas")
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
            print("Obrigado por utilizar o Holmes!!!")
            break
