import os

def normalizar(caminho):
    caminho = caminho.strip()
    caminho = os.path.expandvars(caminho)
    caminho = os.path.normpath(caminho)
    caminho = os.path.normcase(caminho)
    return caminho