import requests
import re
import os

def validar_hash(hash_input):
    if (hash_input != "0"):
        if not hash_input or not hash_input.strip():
            return False

        hash_formatado = hash_input.strip().lower()

        if (len(hash_formatado) != 64):
            return False

        if not re.fullmatch(r"[a-f0-9]{64}", hash_formatado):
            return False
        return True
    else:
        return 0

API_KEY = os.getenv("VI_API_KEY")

cores = {'vermelho':'\033[31m',
         'limpo':'\033[m'}

def verificar_hash():
    print("Regras de utilização da consulta: ")
    print(f"{cores['vermelho']}* Não é permitido realizar mais de 4 consultas por minuto *{cores['limpo']}")
    print(f"{cores['vermelho']}* Apenas é permitido realizar 500 consultas diárias * {cores['limpo']}")
    print(f"{cores['vermelho']}* O hash deve estar no formato SHA256 * {cores['limpo']}")
    while True:
        hash_input = str(input("Insira o hash do executável [insira o valor 0 para voltar ao menu inicial]: "))
        resposta = validar_hash(hash_input)
        if (resposta or resposta == 0):
            break
        else:
            print("Hash inválido.")
    if (resposta != 0):
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

        elif response.status_code == 429:
            return f"{cores['vermelho']}Limite de requisições por minutos atingido. Aguarde 1 minuto e volte a tentar.{cores['limpo']}"

        else:
            return f"Erro: {response.status_code}\n{API_KEY}"
    else:
        return 0
