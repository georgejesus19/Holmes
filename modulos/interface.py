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

def cabecalho(mensagem, tamanho=60):
    """
    :param mensagem: A mensagem que irá aparecer no cabeçalho.
    :param tamanho: largura usada para centralizar o texto.
    :return: Um cabeçalho com linhas e texto em ASCII art.
    """
    f = pyfiglet.Figlet(font="ansi_shadow")

    # Gerar ASCII art
    ascii_art = f.renderText(mensagem.center(tamanho))
    # Limpar linhas em branco no topo e fundo + espaços à direita
    linhas_ascii = ascii_art.splitlines()
    while linhas_ascii and not linhas_ascii[0].strip():
        linhas_ascii.pop(0)
    while linhas_ascii and not linhas_ascii[-1].strip():
        linhas_ascii.pop()
    linhas_ascii = [linha.rstrip() for linha in linhas_ascii]

    ascii_art_limpo = "\n".join(linhas_ascii)

    # Imprimir cabeçalho
    print(linhas(tamanho))
    print(f"{cores['azul']}{ascii_art_limpo}{cores['limpo']}")
    print(linhas(tamanho))

def ler_opcao(mensagem):
    """
    :param mensagem: Mensagem que será apresentada no output.
    :return: O valor correspondente a uma operação.
    """
    opcao = 0
    while True:
        try:
            opcao = int(input(mensagem))
            break
        except ValueError:
            print("Selecione uma opção válida !")
    return opcao
def opcoes():
    lista_opcoes = ["Listar Processos", "Procurar processos suspeitos", "Mostrar programas na chave de registo (HKCU)",
                    "Mostrar Programas na chave de registo (HKLM)", "Procurar programas Suspeitos (HKCU)", "Procurar programas suspeitos (HKLM)",
                    "Listar Tarefas agendadas", "Procurar tarefas agendadas suspeitas", "Listar serviços",
                    "Procurar serviços suspeitos", "Monitorar pasta startup","Verificar Conexões de rede","Verificar Conexões suspeitas de redes", "Sair"]
    for i,opcao in enumerate(lista_opcoes):
        print(f"{i + 1:<2} - {opcao}")

def menu():
    cabecalho("Holmes")
    opcoes()
    print()
    opc = ler_opcao("Selecione a opção: ")
    return opc

