from uteis import variaveis_de_ambiente

def calcular_score_auxiliar(ficheiro, nome_processo, caminho_processo):
    score_local = 0
    motivos_locais = []

    nome_presente = False
    caminho_presente = False

    for valor_processo in ficheiro:
        valor_processo = valor_processo.lower().strip()

        if valor_processo == nome_processo:
            nome_presente = True

        caminho_base = variaveis_de_ambiente.expandir_caminhos(valor_processo)

        if caminho_processo.startswith(caminho_base):
            caminho_presente = True

    if nome_presente and caminho_presente:
        score_local = 60
        motivos_locais.append("Nome e caminho presentes na blacklist")

    elif nome_presente:
        score_local = 40
        motivos_locais.append("Nome presente na blacklist")

    elif caminho_presente:
        score_local = 20
        motivos_locais.append("Caminho presente na blacklist")

    if "system32" in caminho_processo.lower() and nome_presente:
        score_local = max(score_local, 40)
        motivos_locais.append("Execução em System32 com nome suspeito")

    return {'pontuacao': score_local, 'risco': ''}, motivos_locais