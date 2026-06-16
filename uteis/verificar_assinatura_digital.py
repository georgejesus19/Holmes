import subprocess
from CLI import cores
from modulos import logs
from datetime import datetime

assinatura_cache = {}
data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def verificar_assinatura(caminho):
    if caminho in assinatura_cache:
        return assinatura_cache[caminho]
    try:
        raise Exception ("Teste do módulo útil - assinatura digital")
        comando = [
            "powershell",
            "-Command",
            f"(Get-AuthenticodeSignature '{caminho}').Status"
        ]
        resultado = subprocess.run(comando, capture_output=True, text=True)
        status_message = resultado.stdout.strip()

        if status_message not in ['Valid', 'NotSigned', 'HashMismatch', 'NotTrusted']:
            return "UnknownError"

        assinatura_cache[caminho] = status_message
        if resultado.returncode != 0 or resultado.stderr.strip():
            return "UnknownError"
        return status_message

    except Exception as e:
        print(f"{cores.CORES['vermelho']}Ocorreu um erro durante a abertura do ficheiro - blacklist (verificar logs de erro){cores.CORES['limpo']}")
        erro = f"{type(e).__name__}: {e}"
        logs.inserir_log_erro("erro", "uteis", data_atual, erro)
        return "UnknownError"