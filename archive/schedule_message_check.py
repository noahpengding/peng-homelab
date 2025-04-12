from app.utils.rabbitmq_consumer import RabbitMQConsumer
from .message_handler import RabbitMQMessageHandler


def schedule_message_check():
    m = RabbitMQConsumer(group_id="python_homelab", exchange="homelab")
    m.check_message(lambda x: RabbitMQMessageHandler(x))
