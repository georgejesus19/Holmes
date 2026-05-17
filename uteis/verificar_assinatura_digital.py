import subprocess

assinatura_cache = {}

def verificar_assinatura(caminho):
    if caminho in assinatura_cache:
        return assinatura_cache[caminho]
    try:
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
            # O PowerShell teve erro
            #return f"{resultado.stderr.strip()}"
            return "UnknownError"
        return status_message

    except Exception as erro:
        return "UnknownError"