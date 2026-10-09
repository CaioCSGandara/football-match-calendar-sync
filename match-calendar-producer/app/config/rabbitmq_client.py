import os
from typing import Optional
import pika

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class RabbitMQClient:
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        virtual_host: Optional[str] = None
    ):
        # Avalia as variáveis de ambiente na instanciação, com fallbacks seguros
        self.host = host or os.getenv("RABBITMQ_HOST", "localhost")
        self.port = int(port or os.getenv("RABBITMQ_PORT", 5672))
        self.username = username or os.getenv("RABBITMQ_USER", "admin")
        self.password = password or os.getenv("RABBITMQ_PASS", "secret")
        self.virtual_host = virtual_host or os.getenv("RABBITMQ_VHOST", "/")

        self._credentials = pika.PlainCredentials(self.username, self.password)
        self._parameters = pika.ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.virtual_host,
            credentials=self._credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.adapters.blocking_connection.BlockingChannel] = None

    def connect(self) -> pika.adapters.blocking_connection.BlockingChannel:
        """Abre ou reutiliza a conexão e o canal ativo."""
        if not self.connection or self.connection.is_closed:
            self.connection = pika.BlockingConnection(self._parameters)
            self.channel = self.connection.channel()
        elif not self.channel or self.channel.is_closed:
            self.channel = self.connection.channel()
            
        return self.channel

    def declare_exchange(self, exchange: str, exchange_type: str = "direct", durable: bool = True):
        ch = self.connect()
        ch.exchange_declare(exchange=exchange, exchange_type=exchange_type, durable=durable)

    def close(self):
        """Fecha o canal e a conexão de forma idempotente."""
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
        except Exception:
            pass
        finally:
            self.channel = None

        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass
        finally:
            self.connection = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()