def selecionar_valor(lista):
    i = 0
    for i, binario in enumerate(lista):
        print(f"{i + 1} -> Nome: {binario['nome']}")
    total = i

    while True:
        try:
            print("\n* Insira o valor 0 para voltar ao menu inicial * ")
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