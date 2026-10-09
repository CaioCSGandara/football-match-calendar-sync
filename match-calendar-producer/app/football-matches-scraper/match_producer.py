import json
import pika
from app.config.rabbitmq_client import RabbitMQClient

class MatchProducer:
    def __init__(self, rabbit_client: RabbitMQClient, exchange: str = "calendar.matches.sync.exchange", routing_key: str = "matches.scheduled"):
        self.client = rabbit_client
        self.exchange = exchange
        self.routing_key = routing_key
        
        self.client.declare_exchange(self.exchange, exchange_type="topic", durable=True)

    def publish_match(self, match_data: dict):
        channel = self.client.connect()
        
        payload = json.dumps(match_data)
        channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.routing_key,
            body=payload,
            properties=pika.BasicProperties(
                delivery_mode=pika.DeliveryMode.Persistent,
                content_type="application/json"
            )
        )