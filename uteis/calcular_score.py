from heuristica import avaliar_heuristica
from uteis import normalizar_caminho
from uteis import caminho_raiz

def calcular_score_auxiliar(ficheiro, nome, caminho):
    score_local = 0
    motivos_locais = []

    nome_presente = False
    caminho_presente = False

    for valor_processo in ficheiro:
        valor_processo = valor_processo.lower().strip()

        if valor_processo == nome.lower().strip():
            nome_presente = True

        caminho_base = normalizar_caminho.normalizar(valor_processo)

        if caminho.startswith(caminho_base):
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

    if "system32" in caminho.lower() and nome_presente:
        score_local += 30
        motivos_locais.append("Execução em System32 com nome suspeito")

    if (caminho_raiz.verificar_caminho_raiz(caminho)):
        score_local += 25
        motivos_locais.append("Programa na raiz do disco")

    score_heuristica, motivos_heuristica = avaliar_heuristica.avaliar_heuristica_caminho(caminho)
    score_local += score_heuristica
    motivos_locais.extend(motivos_heuristica)

    return {'pontuacao': score_local, 'risco': ''}, motivos_locais