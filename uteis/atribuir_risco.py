def definir_risco(dados_score):
    risco = ''
    if (dados_score['pontuacao'] >= 0 and dados_score['pontuacao'] <= 30):
        risco = 'Baixo'
    elif (dados_score['pontuacao'] > 30 and dados_score['pontuacao'] <= 60):
        risco = 'Médio'
    else:
        risco = 'Alto'
    return risco
