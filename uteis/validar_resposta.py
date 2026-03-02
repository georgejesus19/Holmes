def validar_resposta():
    while True:
        resposta = str(input("Deseja exibir ? [S/N]:")).upper()
        if (resposta not in ["SIM", "S", "N", "NAO", "NÃO"]):
            print("Resposta inválida!")
        else:
            return resposta

