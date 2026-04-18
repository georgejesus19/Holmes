import requests

try:
    response = requests.get("https://httpbin.org/get", timeout=5)
    print(response.json())

    # Verifica se a resposta foi bem-sucedida
    response.raise_for_status()

    # Exibe o status e o conteúdo retornado
    print(f"Status Code: {response.status_code}")
    print("Resposta JSON:")
    print(response.json())


except requests.exceptions.Timeout:
    print("Erro: O servidor demorou muito para responder.")
except requests.exceptions.ConnectionError:
    print("Erro: Não foi possível conectar ao servidor.")
except requests.exceptions.HTTPError as e:
    print(f"Erro HTTP: {e}")
except Exception as e:
    print(f"Ocorreu um erro: {e}")