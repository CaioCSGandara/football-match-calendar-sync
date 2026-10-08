import time
import json
import tls_client

def fetch_all_events():
    session = tls_client.Session(
        client_identifier="firefox_120",
        random_tls_extension_order=True
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:153.0) Gecko/20100101 Firefox/153.0",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Referer": "https://www.sofascore.com/",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Connection": "keep-alive",
    }

    tournament_id = 7
    season_id = 96518
    page = 0
    total_events_collected = 0

    print(f"Iniciando coleta para o torneio {tournament_id}, temporada {season_id}...\n")

    while True:
        url = f"https://www.sofascore.com/api/v1/unique-tournament/{tournament_id}/season/{season_id}/events/next/{page}"
        print(f"--- Requisitando Página {page} ---")

        try:
            response = session.get(url, headers=headers)

            if response.status_code == 200:
                data = response.json()
                events = data.get("events", [])
                has_next_page = data.get("hasNextPage", False)

                if not events:
                    print("Nenhum evento encontrado nesta página. Encerrando.")
                    break

                print(f"Página {page}: {len(events)} eventos retornados.")
                total_events_collected += len(events)

                # Processamento da página atual (aqui entrará o mapper -> fila)
                for event in events:
                    home = event.get("homeTeam", {}).get("name")
                    away = event.get("awayTeam", {}).get("name")
                    match_id = event.get("id")
                    print(f"  [{match_id}] {home} vs {away}")

                # Condição de parada fornecida pela própria API
                if not has_next_page:
                    print("\nAPI indicou que não há mais páginas (`hasNextPage`: False).")
                    break

                page += 1
                time.sleep(10)  # Intervalo de segurança anti-throttling

            elif response.status_code == 404:
                print("Página não encontrada (404). Fim dos eventos disponíveis.")
                break
            else:
                print(f"Resposta inesperada (Status {response.status_code}):")
                print(response.text[:300])
                break

        except Exception as e:
            print(f"Erro inesperado durante a execução da página {page}: {e}")
            break

    print(f"\nColeta finalizada! Total de partidas extraídas: {total_events_collected}")

if __name__ == "__main__":
    fetch_all_events()