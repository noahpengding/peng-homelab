import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.utils.rabbitmq_consumer import RabbitMQConsumer
import app.handlers.message_handler as message_handler

m = RabbitMQConsumer(group_id = "python_homelab", exchange= "homelab")
m.check_message(lambda x: message_handler.RabbitMQMessageHandler(x))
