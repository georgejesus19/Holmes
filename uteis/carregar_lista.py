def carregar_lista(ficheiro):
    lista = []
    try:
        with open(ficheiro, "r", encoding="utf-8") as f:
            for linha in f:
                lista.append(linha.lower().strip())
        return lista
    except (FileNotFoundError, IOError) as erro:
        print(f"Erro ao abrir o ficheiro: {erro}")
        return []