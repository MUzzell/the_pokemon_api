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
        q_type, arg = _parse_request(body.decode("ASCII"))

        result = None
        if q_type == "ID":
            result = self.pokedex.get_pokemon_by_id(arg)
        elif q_type == "NAME":
            result = self.pokedex.get_pokemon_by_name(arg)
        elif q_type == "TYPE":
            result = []
            for p_type in arg.split(','):
                result.append(self.pokedex.get_pokemon_by_type(p_type))

        if not result:
            self._send_error(ch, method, props, 404, "Not found")
        else:
            self._send_result(ch, method, props, result)

    def _send_result(self, ch, method, props, result):
        self._publish(ch, method, props,
                      {'code': 200, 'data': result})

    def _send_error(self, ch, method, props, code, msg):
        self._publish(ch, method, props,
                      {'code': code, 'data': msg})

    def _publish(self, ch, method, props, body):
        ch.basic_publish(
            exchange='', routing_key=props.reply_to,
            properties=pika.BasicProperties(
                correlation_id=props.correlation_id,
                content_encoding='application/json'
            ),
            body=json.dumps(body)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)
