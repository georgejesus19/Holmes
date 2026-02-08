import os
import subprocess

assinatura_cache = {}

def verificar_assinatura(caminho):
    if(os.path.exists(caminho)):
        if caminho in assinatura_cache:
            return assinatura_cache[caminho]
        try:
            comando = [
                "powershell",
                "-Command",
                f"(Get-AuthenticodeSignature '{caminho}').StatusMessage"
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True)
            status_message = resultado.stdout.strip()
            assinatura_cache[caminho] = status_message
            if resultado.returncode != 0 or resultado.stderr.strip():
                # O PowerShell teve erro
                #return f"{resultado.stderr.strip()}"
                return "Erro do powershell"
            return status_message

        except (FileNotFoundError, OSError, subprocess.CalledProcessError, PermissionError, IOError) as erro:
            assinatura_cache[caminho] = f"Erro ao verificar assinatura {erro}"
            return assinatura_cache[caminho]
    else:
        return "Não foi possível verificar assinatura digital (caminho inexistente)"