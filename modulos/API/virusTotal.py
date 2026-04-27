import requests
import re

def validar_hash(hash_input):
    if not hash_input or not hash_input.strip():
        return False

    hash_formatado = hash_input.strip().lower()

    if (len(hash_formatado) != 64):
        return False

    if not re.fullmatch(r"[a-f0-9]{64}", hash_formatado):
        return False

    return True

API_KEY = "teste_key"

def verificar_hash():
    while True:
        hash_input = str(input("Insira o hash do executável (O hash deve estar no formato SHA256): "))
        resposta = validar_hash(hash_input)
        if (resposta):
            break
        else:
            print("Hash inválido.")

    url =  f"https://www.virustotal.com/api/v3/files/{hash_input}"

    headers = {
        "x-apikey": API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()

        stats = data["data"]["attributes"]["last_analysis_stats"]

        return {
            "malicious": stats["malicious"],
            "suspicious": stats["suspicious"],
            "harmless": stats["harmless"],
            "undetected": stats["undetected"]
        }

    elif response.status_code == 404:
        return "Hash não encontrado na base da VirusTotal"

    else:
        return f"Erro: {response.status_code}"
