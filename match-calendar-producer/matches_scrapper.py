import time
from typing import Dict, Any, List, Tuple, Optional
import tls_client

BASE_URL = "https://www.sofascore.com/api/v1"
BASE_HEADERS = {
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


def build_http_session() -> tls_client.Session:
    """Cria e devolve uma sessão tls-client configurada para impersonar o Firefox."""
    return tls_client.Session(
        client_identifier="firefox_120",
        random_tls_extension_order=True
    )


def build_events_url(tournament_id: int, season_id: int, page: int) -> str:
    """Gera a URL parametrizada para paginação dos próximos eventos."""
    return f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/events/next/{page}"


def fetch_events_page(
    session: tls_client.Session, 
    tournament_id: int, 
    season_id: int, 
    page: int
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Executa a requisição HTTP para uma página específica.
    Retorna uma tupla contendo a lista de eventos brutos e o booleano indicando se há próxima página.
    """
    url = build_events_url(tournament_id, season_id, page)
    
    response = session.get(url, headers=BASE_HEADERS)

    if response.status_code == 200:
        data = response.json()
        events = data.get("events", [])
        has_next_page = data.get("hasNextPage", False)
        return events, has_next_page

    if response.status_code == 404:
        print(f"[Page {page}] Fim dos eventos atingido (404 Not Found).")
        return [], False

    raise RuntimeError(
        f"Erro HTTP {response.status_code} na página {page}: {response.text[:200]}"
    )


# def handle_event(raw_event: Dict[str, Any]) -> None:
#     """
#     Trata o evento individual.
#     Ponto de injeção para o mapper e publicação na fila do RabbitMQ.
#     """
#     match_id = raw_event.get("id")
#     home_team = raw_event.get("homeTeam", {}).get("name")
#     away_team = raw_event.get("awayTeam", {}).get("name")
#     timestamp = raw_event.get("startTimestamp")
#     status = raw_event.get("status", {}).get("type")

#     print(f"  -> [{match_id}] {home_team} vs {away_team} | Status: {status} | TS: {timestamp}")


# def crawl_tournament_events(
#     tournament_id: int, 
#     season_id: int, 
#     delay_seconds: int = 10
# ) -> int:
#     """
#     Orquestra a coleta de todas as páginas de um torneio e temporada específicos.
#     Retorna o total de partidas extraídas.
#     """
#     session = build_http_session()
#     page = 0
#     total_events = 0

#     print(f"=== Iniciando coleta do Torneio ID {tournament_id} (Temporada: {season_id}) ===")

#     while True:
#         print(f"Requisitando página {page}...")
        
#         try:
#             events, has_next_page = fetch_events_page(
#                 session=session, 
#                 tournament_id=tournament_id, 
#                 season_id=season_id, 
#                 page=page
#             )
#         except Exception as exc:
#             print(f"[Falha] Interrupção no scraping: {exc}")
#             break

#         if not events:
#             print("Nenhum evento encontrado nesta página.")
#             break

#         # Processamento/Enfileiramento imediato (abordagem streaming)
#         for event in events:
#             handle_event(event)
#             total_events += 1

#         if not has_next_page:
#             print("API indicou que não há mais páginas disponíveis.")
#             break

#         page += 1
#         print(f"Aguardando {delay_seconds}s para evitar rate-limiting...\n")
#         time.sleep(delay_seconds)

#     print(f"=== Concluído. Total de partidas extraídas: {total_events} ===\n")
#     return total_events


# if __name__ == "__main__":
#     CHAMPIONS_LEAGUE_TOURNAMENT_ID = 7
#     CHAMPIONS_LEAGUE_SEASON_ID = 96518

#     crawl_tournament_events(
#         tournament_id=CHAMPIONS_LEAGUE_TOURNAMENT_ID,
#         season_id=CHAMPIONS_LEAGUE_SEASON_ID,
#         delay_seconds=10
#     )