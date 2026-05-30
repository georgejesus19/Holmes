import os
from CLI.cores import CORES
import pyfiglet

def linhas(tamanho=10,tipo="-"):
    """
    :param tamanho: define a quantidade de linhas
    :param tipo: define o tipo de linha a escolha do utilizador(-, -=, *, etc)
    :return: devolve o tipo de linha n vezes.
    """
    return tipo * tamanho

def centralizar_texto(texto):
    try:
        largura_terminal = os.get_terminal_size().columns
    except OSError:
        largura_terminal = 80

    linhas = texto.split("\n")

    # remove linhas vazias no topo/fundo
    linhas = [l for l in linhas if l.strip() != ""]

    # encontra a linha mais larga
    largura_max = max(len(l) for l in linhas)

    resultado = []

    for linha in linhas:
        espacos = max((largura_terminal - largura_max) // 2, 0)
        resultado.append(" " * espacos + linha)

    return "\n".join(resultado)

def cabecalho(mensagem, tamanho=60, modo=""):
    """
    Exibe um cabeçalho em ASCII art colorido.

    :param mensagem: A mensagem que irá aparecer no cabeçalho.
    :param tamanho: largura mínima usada para centralizar o cabeçalho.
    """
    f = pyfiglet.Figlet(font="ansi_shadow")

    # Gerar ASCII art para cada palavra e unir
    palavras = mensagem.split()
    linhas_ascii = []
    for palavra in palavras:
        ascii_palavra = f.renderText(palavra)
        linhas_ascii.extend([linha.rstrip() for linha in ascii_palavra.splitlines() if linha.strip()])

    # Ajustar largura automaticamente
    largura_ascii = max(len(linha) for linha in linhas_ascii)
    largura_final = max(tamanho, largura_ascii)

    # Centralizar cada linha
    linhas_ascii = [linha.center(largura_final) for linha in linhas_ascii]

    # Imprimir cabeçalho
    print(linhas(largura_final))
    print(f"{CORES['azul']}{chr(10).join(linhas_ascii)}{CORES['limpo']}")
    print(linhas(largura_final))
    print(f"\n{CORES['azul']}Modo Atual: {modo}{CORES['limpo']}")
    print(f"{CORES['azul']}Estado: Pronto ✓{CORES['limpo']}")
    print(f"{CORES['azul']}Módulos ativos: Processos | Persistência | Conxões de rede {CORES['limpo']}")
    if (modo == "Análise Manual"):
        print(f"{CORES['azul']}Funcionalidades adicioneis: Consulta a API | Consulta de logs{CORES['limpo']}")
    print(f"{CORES['azul']}Versão: 1.0.0 {CORES['limpo']}\n")
    print(linhas(largura_final))


def ler_opcao(mensagem, limite=15):
    """
    :param mensagem: Mensagem que será apresentada no output.
    :return: O valor correspondente a uma operação.
    """
    opcao = 0
    while True:
        try:
            opcao = int(input(mensagem))
            if ((opcao > limite) or (opcao <= 0)):
                print("Selecione uma opção válida !")
            else:
                break
        except ValueError:
            print("Selecione uma opção válida !")
    return opcao

def opcoes():
    lista_opcoes = ["Listar Processos", "Mostrar programas na chave de registo (HKCU)", "Mostrar Programas na chave de registo (HKLM)",
                    "Listar Tarefas agendadas", "Listar serviços","Monitorar pasta startup",
                    "Verificar Conexões de rede", "Modo Manual", "Sair"]
    for i,opcao in enumerate(lista_opcoes):
        print(f"[{i + 1}] - {opcao}")

def opcoes_modo_manual():
    lista_opcoes = ["Analisar processo", "Analisar Programa na chave de registo (HKCU)", "Analisar Programa na chave de registo (HKLM)" ,"Analisar tarefa agendada",
                    "Analisar Serviço", "Analisar Conexão de rede","Consultar Hash (API VirusTotal)", "Exibir processos registados na DB", "Exibir programas (HKCU) registados na DB",
                    "Exibir programas (HKLM) registados na DB", "Exibir tarefas agendadas registadas na DB", "Exibir serviços registados na DB","Exibir conexões de rede registadas na DB", "Voltar"]
    for i, opcao in enumerate(lista_opcoes):
        if (i + 1 <= 9):
            print(f"[{i + 1}]  - {opcao}")
        else:
            print(f"[{i + 1}] - {opcao}")

def menu():
    cabecalho("Holmes", modo="Análise Automática")
    opcoes()
    print()
    print(linhas(tamanho=60))
    opc = ler_opcao("Selecione a opção: ", 9)
    return opc

def menu_modo_manual():
    cabecalho("Holmes", modo="Análise Manual")
    opcoes_modo_manual()
    print()
    print(linhas(tamanho=60))
    opc = ler_opcao("Selecione uma opção: ", 14)
    return opc

def menu_inicial():
    holmes_icon = f"""
                                   ████████████████████                                   
                            ███████████            ███████████                            
                        ███████                             ███████                       
                    ██████                                       █████                    
                 █████                                              █████                 
               ████                             ██  ██                 █████              
             ███                          ████████████                    ████            
           ███                         ██████████████████                   ████          
         ███                          █████████████████████                   ███         
       ████                         ████████████████████████                    ███       
      ███                           █████████████████████████                    ███      
     ███                          ███████████████████████████                     ███     
    ███                        ██████████████████████████████                       ███   
   ███                        ███████████████████████████████                       ███   
  ███                             ████████████████████████████                       ███  
  ██                             ██████████████████████████████                       ███ 
 ███                                ███████████████████                                ██ 
 ██            ██                    ███████████████     ███                           ███
███           ███  █                 █████████████    ███████                          ███
███           ███                    ██████████    ███████████                         ███
███            ██   █                 ███████   ████████████████                        ██
███            ███   █                        ██████████████████                        ██
███             ██   █                     ████████████████████████                    ███
███             ███   █                  ████████████████████████████                  ███
 ██              ███  █                ████████████████████████████████                ███
 ███               ███                ██████████████████████████████████              ███ 
  ███               ███             ██████████████████████████████████████            ███ 
  ███                ██            ████████████████████████████████████████          ███  
   ███                ██                ████████████████████████████████████        ███   
    ███               ███         ███████████████████████████████████████████      ███    
     ███               ██       █████████████████████████████████████████████     ███     
      ███                      ███████████████████████████████████████████       ███      
        ███                   ██████████████████████████████████████████       ████       
         ████                ████████████████████████████████████████         ███         
           ████             █████████████████████████████████████           ███           
             ████          █████████████████████████████████              ███             
               ████        ███████████████████████████                 ████               
                  █████                                             █████                 
                     ██████                                     █████                     
                         ███████                          ████████                        
                             ████████████████████████████████                             
                                     ████████████████ 
     """
    print(f"{CORES['azul']}")
    print(centralizar_texto(holmes_icon))
    print(f"{CORES['limpo']}")
    print(centralizar_texto(" > Holmes: Detector de Backdoors."))
    print(centralizar_texto(" > Criado por: George de Jesus Hebo"))
    print(centralizar_texto(" > Versão: 1.0.0"), "\n\n")
    input(centralizar_texto("Pressione enter para continuar..."))