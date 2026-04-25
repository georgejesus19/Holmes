import requests

API_KEY = "teste_key"

def verificar_hash(hash):
    url =  f"https://www.virustotal.com/api/v3/files/{hash}"

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

print(verificar_hash("9b51ae08b09c167582b9dd29007a96a67f016958ed3d47b1273bdd4a7385fb50"))
