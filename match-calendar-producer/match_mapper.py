import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class MatchEvent:
    """Modelo canônico que representa uma partida no ecossistema interno."""
    match_id: int
    tournament_id: int
    tournament_name: str
    season_id: int
    round_number: Optional[int]
    status: str
    start_timestamp: int
    start_time_iso: str
    home_team_id: int
    home_team_name: str
    away_team_id: int
    away_team_name: str
    home_score: Optional[int] = None
    away_score: Optional[int] = None

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
        # Extração de IDs e dados do torneio
        match_id = int(raw_event["id"])
        
        tournament_info = raw_event.get("tournament", {})
        unique_tournament = tournament_info.get("uniqueTournament", {})
        tournament_id = int(unique_tournament.get("id") or tournament_info.get("id", 0))
        tournament_name = unique_tournament.get("name") or tournament_info.get("name", "Unknown")

        season_id = int(raw_event.get("season", {}).get("id", 0))
        round_info = raw_event.get("roundInfo", {})
        round_number = round_info.get("round")

        # Status e Horário
        status_info = raw_event.get("status", {})
        status = status_info.get("type", "unknown").lower()

        start_ts = int(raw_event["startTimestamp"])
        start_iso = datetime.fromtimestamp(start_ts, tz=timezone.utc).isoformat()

        # Equipes
        home_team = raw_event.get("homeTeam", {})
        away_team = raw_event.get("awayTeam", {})

        home_team_id = int(home_team["id"])
        home_team_name = str(home_team.get("name", "Unknown"))
        
        away_team_id = int(away_team["id"])
        away_team_name = str(away_team.get("name", "Unknown"))

        # Placar (se a partida já começou ou terminou)
        home_score_data = raw_event.get("homeScore", {})
        away_score_data = raw_event.get("awayScore", {})
        
        home_score = home_score_data.get("current")
        away_score = away_score_data.get("current")

        return MatchEvent(
            match_id=match_id,
            tournament_id=tournament_id,
            tournament_name=tournament_name,
            season_id=season_id,
            round_number=int(round_number) if round_number is not None else None,
            status=status,
            start_timestamp=start_ts,
            start_time_iso=start_iso,
            home_team_id=home_team_id,
            home_team_name=home_team_name,
            away_team_id=away_team_id,
            away_team_name=away_team_name,
            home_score=int(home_score) if home_score is not None else None,
            away_score=int(away_score) if away_score is not None else None
        )