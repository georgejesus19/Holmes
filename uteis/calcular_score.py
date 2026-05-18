from uteis import variaveis_de_ambiente

def calcular_score_auxiliar(ficheiro, nome_processo, caminho_processo):
    dados_score = {'pontuacao': 0, 'risco': ''}  # armazena todos os processos.txt considerados suspeitos.
    motivos = []

    score_local = 0
    motivos_locais = []

    nome_achado = False
    caminho_achado = False
    nome_presente = False
    caminho_presente = False

    for valor_processo in ficheiro:
        valor_processo = valor_processo.lower().strip()

        if not nome_achado:
            if (valor_processo == nome_processo):
                nome_presente = True
                nome_achado = True

        if not caminho_achado:
            if (caminho_processo.startswith(variaveis_de_ambiente.expandir_caminhos(valor_processo))):
                caminho_presente = True
                caminho_achado = True

        if (nome_presente and caminho_presente):
            score_local = 60
            motivos_locais = ["Nome e caminho presentes na blacklist"]
            break

        elif (nome_presente):
            score_local = 40
            motivos_locais = ["Nome presente na blacklist"]

        elif (caminho_presente):
            score_local = 40
            motivos_locais = ["Caminho presente na blacklist"]

    dados_score['pontuacao'] += score_local
    motivos.extend(motivos_locais)

    return dados_score, motivos