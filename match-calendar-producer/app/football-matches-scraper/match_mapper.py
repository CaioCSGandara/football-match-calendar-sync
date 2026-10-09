import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class MatchEvent:
    """Modelo canônico que representa uma partida no ecossistema interno."""
    match_id: Optional[int] = None
    tournament_name: Optional[str] = None
    tournament_slug: Optional[str] = None
    season_year: Optional[str] = None
    round_number: Optional[int] = None
    status: Optional[str] = None
    venue_name: Optional[str] = None
    venue_slug: Optional[str] = None
    venue_city: Optional[str] = None
    venue_country: Optional[str] = None
    home_team_name: Optional[str] = None
    away_team_name: Optional[str] = None
    start_timestamp: Optional[int] = None
    start_time_iso: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte a dataclass para dicionário nativo."""
        return asdict(self)

    def to_json(self) -> str:
        """Serializa o modelo para string JSON pronta para a fila do RabbitMQ."""
        return json.dumps(self.to_dict(), ensure_ascii=False)


class MatchMapper:
    """
    Camada Anti-Corrupção (ACL).
    Responsável por achatar e sanitizar a estrutura bruta vinda do Sofascore.
    """

    @staticmethod
    def from_sofascore(raw_event: Dict[str, Any]) -> MatchEvent:
        """
        Recebe o dict de um evento retornado pela API do Sofascore
        e constrói a instância canônica validada.
        """
        match_id = raw_event.get("id")
        if match_id is not None:
            try:
                match_id = int(match_id)
            except (ValueError, TypeError):
                match_id = None

        # Torneio
        tournament = raw_event.get("tournament") or {}
        tournament_name = tournament.get("name")
        tournament_slug = tournament.get("slug")

        # Temporada
        season = raw_event.get("season") or {}
        season_year = season.get("year")
        if season_year is not None:
            season_year = str(season_year)

        # Rodada
        round_info = raw_event.get("roundInfo") or {}
        round_number = round_info.get("round")
        if round_number is not None:
            try:
                round_number = int(round_number)
            except (ValueError, TypeError):
                round_number = None

        # Status
        status_info = raw_event.get("status") or {}
        status = status_info.get("type")
        if status is not None:
            status = str(status).lower()

        # Localização (Venue)
        venue = raw_event.get("venue") or {}
        venue_name = venue.get("name")
        venue_slug = venue.get("slug")

        city = venue.get("city") or {}
        venue_city = city.get("name")

        country = city.get("country") or {}
        venue_country = country.get("name")

        # Equipes
        home_team = raw_event.get("homeTeam") or {}
        home_team_name = home_team.get("name")

        away_team = raw_event.get("awayTeam") or {}
        away_team_name = away_team.get("name")

        # Data e Hora
        start_ts = raw_event.get("startTimestamp")
        start_time_iso = None
        if start_ts is not None:
            try:
                start_ts = int(start_ts)
                start_time_iso = datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat()
            except (ValueError, TypeError):
                start_ts = None

        return MatchEvent(
            match_id=match_id,
            tournament_name=tournament_name,
            tournament_slug=tournament_slug,
            season_year=season_year,
            round_number=round_number,
            status=status,
            venue_name=venue_name,
            venue_slug=venue_slug,
            venue_city=venue_city,
            venue_country=venue_country,
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            start_timestamp=start_ts,
            start_time_iso=start_time_iso,
        )