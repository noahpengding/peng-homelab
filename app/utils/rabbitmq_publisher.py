import pika
import json
import uuid
from typing import Dict, Any
from app.config.config import config
from app.utils.log import output_log

class RabbitMQPublisher:
    def __init__(self):
        output_log(f"RabbitMQPublisher: {config.rabbitmq_url}", 'debug')
        self.connection = pika.BlockingConnection(pika.URLParameters(config.rabbitmq_url))
        self.channel = self.connection.channel()
        
    def publish(self, message: Dict[str, Any], exchange: str = config.rabbitmq_exchangeout):
        self.channel.exchange_declare(
            exchange=exchange,
            exchange_type='fanout', 
            durable=True
        )
        body = {
            "ID": str(uuid.uuid4()),
            "Topic": exchange,
            "Data": message,
            "Channel": config.rabbitmq_exchangedefault
        }
        output_log(f"Publishing message: {body}", 'debug')
        self.channel.basic_publish(
            exchange=body["Topic"], 
            routing_key='', 
            body=json.dumps(body),
            properties=pika.BasicProperties(
                delivery_mode=2,
                message_id=body["ID"],
                content_type='application/json'
            )
        )
    
    def close(self):
        self.connection.close()