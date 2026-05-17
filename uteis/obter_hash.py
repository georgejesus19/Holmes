import os
import hashlib

def obter_hash(caminho, tipo_hash="sha256"):
    hash_func = hashlib.new(tipo_hash)
    try:
        with open(caminho, "rb") as ficheiro:
            for p in iter(lambda: ficheiro.read(4096), b""):
                hash_func.update(p)
        return hash_func.hexdigest()
    except Exception as erro:
        return f"Erro durante a obtenção do hash"