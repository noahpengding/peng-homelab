import app.rabbitmq_publisher as rabbitmq_publisher

if __name__ == '__main__':
    r = rabbitmq_publisher.RabbitMQPublisher()
    r.publish("Hello World")