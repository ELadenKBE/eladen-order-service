import json

import pika as pika
from pika import PlainCredentials
from pika.exceptions import StreamLostError

from orders.models import Order
from decouple import config
from django.forms.models import model_to_dict




class CheckoutProducer:
    connection_params = None
    connection = None
    channel = None

    def __init__(self):
        self.connect()

    def connect(self):
        local_mode = config('LOCAL_MODE', default=False, cast=bool)
        # if local_mode:
        #     print("Local mode is on! connection to rabbitmq is off")
        #     return
        username = config('RABBITMQ_USERNAME', default="admin", cast=str)
        password = config('RABBITMQ_PASSWORD', default="12345", cast=str)
        host = config('RABBITMQ_HOST', default="rabbitmq", cast=str)
        connection_params = pika.ConnectionParameters(
            host=host, credentials=PlainCredentials(username=username,
                                                    password=password))
        self.connection = pika.BlockingConnection(connection_params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='checkout_queue')

    def publish_order(self, order: Order):
        message = json.dumps(model_to_dict(order))
        try:
            self.channel.basic_publish(exchange='',
                                       routing_key='checkout_queue',
                                       body=message)
        except StreamLostError as e:
            self.connect()
            self.publish_order(order)
        except Exception as e:
            pass

