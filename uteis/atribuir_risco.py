def definir_risco(dados_score):
    score = dados_score['pontuacao']

    if score <= 39:
        return 'Baixo'
    elif score <= 59:
        return 'Médio'
    else:
        return 'Alto'