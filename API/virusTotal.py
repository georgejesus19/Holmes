import re
import os
import requests
from CLI import painel
from CLI import cores
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HOLMES_API_KEY")

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

def verificar_hash():
    painel.painel_consulta_hash()
    while True:
        hash_input = str(input("Insira o hash do executável [insira o valor 0 para voltar ao menu inicial]: ")).strip()
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
                "undetected": stats["undetected"],
                "hash": hash_input
            }

        elif response.status_code == 404:
            return "Hash não encontrado na base da VirusTotal"

        elif response.status_code == 429:
            return f"{cores.CORES['vermelho']}Limite de requisições por minutos atingido. Aguarde 1 minuto e volte a tentar.{cores.CORES['limpo']}"

        else:
            return f"Erro: {response.status_code}\n{API_KEY}"
    else:
        return 0