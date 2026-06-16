import hashlib
from CLI import cores
from modulos import logs
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def obter_hash(caminho, tipo_hash="sha256"):
    hash_func = hashlib.new(tipo_hash)
    try:
        with open(caminho, "rb") as ficheiro:
            for p in iter(lambda: ficheiro.read(4096), b""):
                hash_func.update(p)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a obtenção do hash (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "uteis", data_atual, erro)
        return f"Erro durante a obtenção do hash"