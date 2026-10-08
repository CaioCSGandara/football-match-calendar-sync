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