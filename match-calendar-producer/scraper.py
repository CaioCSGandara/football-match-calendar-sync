import time
import json
import tls_client

def fetch_sofascore_events():
    # Cria uma sessão configurada especificamente para OkHttp 4 no Android 13
    session = tls_client.Session(
        client_identifier="okhttp4_android_13",
        random_tls_extension_order=True
    )

    pageNumber = 0

    while True:

        url = f"https://api.sofascore.com/api/v1/unique-tournament/325/season/87678/events/next/{pageNumber}"

        # Timestamp dinâmico atual em milissegundos
        current_timestamp = str(int(time.time() * 1000))

        headers = {
            "user-agent": "com.sofascore.results/260817/1c992f",
            "x-timestamp": current_timestamp,
            "cache-control": "max-age=0",
            "accept-encoding": "gzip",
            "accept": "application/json",
        }

        try:
            response = session.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                print(f"Sucesso! Total de eventos encontrados: {len(events)}\n")
                hasNextPage = data.get("hasNextPage")
                print(f"Próxima página disponível: {hasNextPage}\n")

                # Exibe primeiros jogos como validação
                for event in events:
                    home = event.get("homeTeam", {}).get("name")
                    away = event.get("awayTeam", {}).get("name")
                    start = event.get("startTimestamp")
                    status = event.get("status", {}).get("type")
                    print(f"-> {home} vs {away} | Status: {status} | Timestamp: {start}")
            else:
                print("Resposta recebida (não-200):")
                print(response.text)

        except Exception as e:
            print(f"Erro durante a execução: {e}")  

        if not hasNextPage:
            print("Não há mais páginas disponíveis. Encerrando a execução.")
            break

        pageNumber += 1
        time.sleep(5)  # Pausa de 1 segundo entre as requisições para evitar sobrecarga
        print(f"Passando para a página {pageNumber + 1}")
if __name__ == "__main__":
    fetch_sofascore_events()