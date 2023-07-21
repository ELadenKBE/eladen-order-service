import json

import pika as pika

from orders.models import Order
from decouple import config
from django.forms.models import model_to_dict

host = config('RABBITMQ_HOST', default="localhost", cast=str)


class CheckoutProducer:
    connection_params = pika.ConnectionParameters(host)
    connection = pika.BlockingConnection(connection_params)
    channel = connection.channel()
    channel.queue_declare(queue='checkout_queue')

    def publish_order(self, order: Order):
        message = json.dumps(model_to_dict(order))
        self.channel.basic_publish(exchange='',
                                   routing_key='checkout_queue',
                                   body=message)
        self.connection.close()
