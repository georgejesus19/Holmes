import hashlib

def obter_hash(caminho, tipo_hash="sha256"):
    hash_func = hashlib.new(tipo_hash)
    try:
        with open(caminho, "rb") as ficheiro:
            for p in iter(lambda: ficheiro.read(4096), b""):
                hash_func.update(p)
        return hash_func.hexdigest()
    except (FileNotFoundError, IOError, NameError) as erro:
        #print(f"Erro durante a obtenção do hash: {erro}")
        return f"Erro durante a obtenção do hash"