from pathlib import Path

def verificar_caminho_raiz(caminho):
    p = Path(caminho)
    parent_str = str(p.parent).replace("/", "\\")
    return (p.suffix.lower() == ".exe" and parent_str == p.anchor)