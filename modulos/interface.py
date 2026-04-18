import pyfiglet

cores = {'limpo':'\033[m',
          'azul':'\033[34m'}

def linhas(tamanho=10,tipo="-"):
    """
    :param tamanho: define a quantidade de linhas
    :param tipo: define o tipo de linha a escolha do utilizador(-, -=, *, etc)
    :return: devolve o tipo de linha n vezes.
    """
    return tipo * tamanho


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
    print(f"{cores['azul']}{chr(10).join(linhas_ascii)}{cores['limpo']}")
    print(f"\n\n{cores['azul']}Modo: {modo}{cores['limpo']}")
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
    lista_opcoes = ["Listar Processos", "Procurar processos suspeitos", "Mostrar programas na chave de registo (HKCU)",
                    "Mostrar Programas na chave de registo (HKLM)", "Procurar programas Suspeitos (HKCU)", "Procurar programas suspeitos (HKLM)",
                    "Listar Tarefas agendadas", "Procurar tarefas agendadas suspeitas", "Listar serviços",
                    "Procurar serviços suspeitos", "Monitorar pasta startup","Verificar Conexões de rede","Verificar Conexões suspeitas de redes", "Modo Manual","Sair"]
    for i,opcao in enumerate(lista_opcoes):
        print(f"{i + 1:<2} - {opcao}")

def opcoes_modo_manual():
    lista_opcoes = ["Analisar processo", "Analisar Programa na chave de registo", "Analisar tarefa agendada",
                    "Analisar Serviço", "Analisar Conexão de rede","Consultar Hash (API VirusTotal)", "Exibir processos registados na DB",
                    "Exibir processos suspeitos registados na DB", "Exibir programas (HKCU) registados na DB", "Exibir programas suspeitos (HKCU) na DB",
                    "Exibir programas (HKLM) registados na DB", "Exibir programas suspeitos (HKLM) na DB", "Exibir tarefas agendadas registadas na DB",
                    "Exibir tarefas agendadas suspeitas registadas na DB", "Exibir serviços registados na DB", "Exibir serviços suspeitos registados na DB",
                    "Exibir conexões registadas na DB", "Exibir conexões suspeitas registadas na DB", "Voltar"]
    for i, opcao in enumerate(lista_opcoes):
        print(f"{i + 1:<2} - {opcao}")


def menu():
    cabecalho("Holmes", modo="Análise Automática")
    opcoes()
    print()
    opc = ler_opcao("Selecione a opção: ")
    return opc

def menu_modo_manual():
    cabecalho("Holmes", modo="Análise Manual")
    opcoes_modo_manual()
    print()
    opc = ler_opcao("Selecione uma opção: ", 19)
    return opc



def menu_inicial():
    print(f"""{cores['azul']}

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
     {cores['limpo']}""")
    input("Pressione enter para continuar...")