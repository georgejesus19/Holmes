from CLI import cores
def definir_risco(dados_score):
    risco = ''
    if (dados_score['pontuacao'] >= 0 and dados_score['pontuacao'] <= 30):
        risco = f'{cores.CORES['verde']}Baixo{cores.CORES['limpo']}'
    elif (dados_score['pontuacao'] > 30 and dados_score['pontuacao'] <= 60):
        risco = f'{cores.CORES['amarelo']}Médio{cores.CORES['limpo']}'
    else:
        risco = f'{cores.CORES['vermelho']}Alto{cores.CORES['limpo']}'
    return risco
