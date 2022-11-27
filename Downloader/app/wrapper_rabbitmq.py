import pika

class RabbitMQ:
    
    def __init__(self, 
                rabbit_pass,
                rabbit_host,
                rabbit_user,
                ) -> None:
        self.connection = None
        self.rabbit_pass = rabbit_pass
        self.rabbit_host = rabbit_host
        self.rabbit_user = rabbit_user

    def getConnectionRabbitMQ(self):
        credentials = pika.PlainCredentials(self.rabbit_user, self.rabbit_pass)
        parameters = pika.ConnectionParameters(host=self.rabbit_host, credentials=credentials, heartbeat=600) 
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        return channel
