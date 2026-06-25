def avaliar_heuristica_caminho(caminho):

    score = 0
    motivos = []

    c = caminho.lower().strip()

    if ("startup" in c or "tasks" in c or "programdata\\microsoft\\windows" in c):
        score += 30
        motivos.append("Possível persistência do sistema ou serviço")

    elif ("appdata" in c or "locallow" in c or
          "notifications" in c or "explorer" in c):
        score += 20
        motivos.append("Execução em diretório comum a malwares/persistência")

    elif ("temp" in c or "tmp" in c):
        score += 15
        motivos.append("Execução em diretório temporário")

    return score, motivos