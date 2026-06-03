from modulos import interface

def selecionar_valor(lista, tamanho):
    i = 0
    for i, binario in enumerate(lista):
        print(f"[{i + 1}]   {binario['nome']}")

    total = i

    while True:
        try:
            print("\n")
            print(interface.linhas(tamanho + 10, "_"), "\n")
            print("Insira o valor 0 para voltar ao menu inicial \n")
            print(interface.linhas(tamanho + 10, "_"), "\n")
            opc = int(input(f"Selecione um valor entre 1 e {total + 1}: "))
            if (((opc - 1) > total) or (opc < 0)):
                print("Selecione uma opção válida!")
            elif (opc == 0):
                return 0
            else:
                break
        except (ValueError):
            print("Selecione uma opção válida!")
    return lista[opc - 1]