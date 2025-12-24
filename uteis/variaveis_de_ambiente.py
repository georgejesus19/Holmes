import os

def expandir_caminhos(ficheiro):
    try:
        with open(ficheiro, "r") as blacklist:
            for linha in blacklist:
                if ("%" in linha):
                    expandida = os.path.expandvars(linha.strip())
                    return os.path.normpath(expandida)
    except (FileNotFoundError, OSError, PermissionError) as error:
        print(f"Ocorreu um erro ao expandir a variavel, erro: {error}")
#expandir_caminhos("../listas/teste.txt")


