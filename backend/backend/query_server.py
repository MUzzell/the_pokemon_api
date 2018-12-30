import pika
import json


def _parse_request(message):
    return message.split(":")


class QueryServer(object):

    def __init__(self, query_queue, pokedex):
        self.query_queue = query_queue
        self.pokedex = pokedex

    def setup(self, channel):
        channel.queue_declare(queue=self.query_queue)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.handle_request, queue=self.query_queue)

    def handle_request(self, ch, method, props, body):
        print("Got Query Request")
        q_type, arg = _parse_request(body.decode("ASCII"))

        result = None
        if q_type == "ID":
            result = self.pokedex.get_pokemon_by_id(arg)
        elif q_type == "NAME":
            result = self.pokedex.get_pokemon_by_name(arg)

        ch.basic_publish(
            exchange='', routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id
            ),
            body=json.dumps(result)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
