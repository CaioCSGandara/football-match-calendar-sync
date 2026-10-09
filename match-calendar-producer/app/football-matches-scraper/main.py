import os
import sys
from pathlib import Path
import time
from datetime import datetime
from typing import List, Dict, Any

# Adiciona o diretório raiz do projeto ao sys.path para permitir importações do pacote 'app'
ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from match_scrapper import build_http_session, fetch_events_page, fetch_latest_season_id
from match_mapper import MatchMapper
from app.config.rabbitmq_client import RabbitMQClient
from match_producer import MatchProducer
from app.utils.yaml_reader import read_yaml

TOURNAMENTS_FILE_PATH = Path(__file__).parent / "tournaments.yaml"

# Configuração dos torneios a serem monitorados (carregada do tournaments.yaml)
TOURNAMENTS_CONFIG: List[Dict[str, Any]] = read_yaml(TOURNAMENTS_FILE_PATH).get("tournaments", [])

PAGE_DELAY_SECONDS = int(os.getenv("SCRAPER_PAGE_DELAY", "15"))

scheduler = BlockingScheduler(timezone="America/Sao_Paulo")


@scheduler.scheduled_job(IntervalTrigger(seconds=600))
def run_pipeline():
    start_time = datetime.now()
    print(f"\n[{start_time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando ciclo do pipeline...")

    # Garante fechamento limpo da conexão e canal com RabbitMQ ao fim de cada ciclo
    with RabbitMQClient() as rabbit_client:
        producer = MatchProducer(rabbit_client=rabbit_client)
        session = build_http_session()

        total_published = 0

        for tournament in TOURNAMENTS_CONFIG:
            t_name = tournament["name"]
            t_id = tournament["tournament_id"]

            try:
                s_id = fetch_latest_season_id(tournament_id=t_id, session=session)
            except Exception as exc:
                print(f"[{t_name}] Falha ao capturar a temporada mais recente: {exc}")
                continue

            print(f"\n--- Iniciando coleta: {t_name} (Torneio: {t_id}, Temporada: {s_id}) ---")
            page = 0

            while True:
                try:
                    events, has_next_page = fetch_events_page(
                        session=session,
                        tournament_id=t_id,
                        season_id=s_id,
                        page=page
                    )
                except Exception as exc:
                    print(f"[{t_name} | Página {page}] Falha na extração HTTP: {exc}")
                    break

                if not events:
                    print(f"[{t_name}] Nenhum evento retornado na página {page}. Encerrando torneio.")
                    break

                # Mapeia e publica na fila mensagem por mensagem (streaming)
                for raw_event in events:
                    try:
                        match_event = MatchMapper.from_sofascore(raw_event)
                        producer.publish_match(match_event.to_dict())
                        total_published += 1
                    except Exception as err:
                        match_id = raw_event.get("id", "desconhecido")
                        print(f"  [Erro Mapper/Publish] Partida ID {match_id}: {err}")

                print(f"  Página {page} processada: {len(events)} jogos enfileirados.")

                if not has_next_page:
                    print(f"[{t_name}] Última página atingida.")
                    break

                page += 1
                time.sleep(PAGE_DELAY_SECONDS)

    elapsed = (datetime.now() - start_time).total_seconds()
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Ciclo finalizado com sucesso!")
    print(f"Total de mensagens enviadas: {total_published} em {elapsed:.2f}s.\n")


if __name__ == "__main__":
    print("Iniciando scheduler do Homelab (Job a cada 600s)...")
    try:
        # Executa imediatamente a primeira vez ao iniciar o container
        run_pipeline()
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler encerrado pelo usuário.")
        scheduler.shutdown()