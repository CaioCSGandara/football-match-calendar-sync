import time
from typing import Dict, Any, List, Tuple, Optional
import tls_client

from browser_utils import get_random_browser_profile

BASE_URL = "https://www.sofascore.com/api/v1"

BASE_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Referer": "https://www.sofascore.com/",
    "Sec-Fetch-Site": "same-origin",
    "Priority": "u=4",
    "Connection": "keep-alive",
}


def build_headers(user_agent: Optional[str] = None) -> Dict[str, str]:
    """Gera o dicionário de cabeçalhos HTTP com o User-Agent especificado ou aleatório."""
    headers = BASE_HEADERS.copy()
    ua = user_agent or get_random_browser_profile()["user_agent"]
    headers["User-Agent"] = ua
    return headers


def build_http_session(client_identifier: Optional[str] = None) -> tls_client.Session:
    """Cria e devolve uma sessão tls-client configurada com client_identifier aleatório ou especificado."""
    cid = client_identifier or get_random_browser_profile()["client_identifier"]
    return tls_client.Session(
        client_identifier=cid,
        random_tls_extension_order=True
    )


def build_events_url(tournament_id: int, season_id: int, page: int) -> str:
    """Gera a URL parametrizada para paginação dos próximos eventos."""
    return f"{BASE_URL}/unique-tournament/{tournament_id}/season/{season_id}/events/next/{page}"


def fetch_events_page(
    session: Optional[tls_client.Session] = None, 
    tournament_id: int = 0, 
    season_id: int = 0, 
    page: int = 0
) -> Tuple[List[Dict[str, Any]], bool]:
    """
    Executa a requisição HTTP para uma página específica.
    A cada iteração (chamada da função), seleciona aleatoriamente um par de (client_identifier, user_agent)
    para criar uma sessão de TLS e cabeçalhos correspondentes, prevenindo bloqueios anti-bot.
    Retorna uma tupla contendo a lista de eventos brutos e o booleano indicando se há próxima página.
    """
    profile = get_random_browser_profile()
    
    # Cria uma sessão com o client_identifier sorteado para essa requisição
    active_session = tls_client.Session(
        client_identifier=profile["client_identifier"],
        random_tls_extension_order=True
    )
    headers = build_headers(profile["user_agent"])

    url = build_events_url(tournament_id, season_id, page)
    
    response = active_session.get(url, headers=headers)

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