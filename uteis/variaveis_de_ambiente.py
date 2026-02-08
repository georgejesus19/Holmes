import os
from pathlib import Path

def expandir_caminhos(caminho):
    if not caminho:
        return None
    caminho = caminho.strip()
    if "%" in caminho:
        caminho = os.path.expandvars(caminho)
    caminho = os.path.normpath(caminho)
    caminho = os.path.normcase(caminho)
    return caminho