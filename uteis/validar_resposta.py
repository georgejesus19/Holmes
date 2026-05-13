def validar_resposta(texto):
    while True:
        resposta = str(input(f"{texto} ? [S/N]:")).upper()
        if (resposta not in ["SIM", "S", "N", "NAO", "NÃO"]):
            print("Resposta inválida!")
        else:
            return resposta