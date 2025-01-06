import pika
import json
import uuid
from typing import Dict, Any
from app.config import config

class RabbitMQPublisher:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.URLParameters(config.rabbitmq_url))
        self.channel = self.connection.channel()
        
    def publish(self, message: Dict[str, Any]):
        self.channel.exchange_declare(
            exchange=config.rabbitmq_exchangeout,
            exchange_type='fanout', 
            durable=True
        )
        body = {
            "ID": str(uuid.uuid4()),
            "Topic": config.rabbitmq_exchangeout,
            "Data": message,
            "Channel": "Homelab"
        }
        self.channel.basic_publish(
            exchange=body["Topic"], 
            routing_key='', 
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=2,
                message_id=body["ID"]
            )
        )
    
    def close(self):
        self.connection.close()