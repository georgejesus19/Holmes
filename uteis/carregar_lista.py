from CLI import cores
from modulos import logs
from datetime import datetime

data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def carregar_lista(ficheiro):
    lista = []
    try:
        with open(ficheiro, "r", encoding="utf-8") as f:
            for linha in f:
                lista.append(linha.lower().strip())
        return lista
    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a abertura do ficheiro - blacklist (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "uteis", data_atual, erro)
        return []