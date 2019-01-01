import pika
import json
import re

STATS_REGEX = re.compile("([a-zA-Z0-9]+)([<>=]{1,2})(\\d+)")

def _parse_request(message):
    return message.split(":")


class QueryServer(object):

    def __init__(self, query_queue, pokedex):
        self.query_queue = query_queue
        self.pokedex = pokedex

        self.q_func = {
            'ID': self._get_by_id,
            'NAME': self._get_by_name,
            'TYPE': self._get_by_type,
            'GEN': self._get_by_gen,
            'LEGEND': self._get_by_legendary,
            'STATS': self._get_by_stats
        }

    def setup(self, channel):
        channel.queue_declare(queue=self.query_queue)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.handle_request, queue=self.query_queue)

    def handle_request(self, ch, method, props, body):
        q_type, arg = _parse_request(body.decode("ASCII"))

        result = self.q_func[q_type](arg)

        if not result:
            self._send_error(ch, method, props, 404, "Not found")
        else:
            self._send_result(ch, method, props, result)

    def _get_by_id(self, arg):
        return self.pokedex.get_pokemon_by_id(arg)

    def _get_by_name(self, arg):
        return self.pokedex.get_pokemon_by_name(arg)

    def _get_by_gen(self, arg):
        return self.pokedex.get_pokemon_by_generation(arg)

    def _get_by_legendary(self, arg):
        return self.pokedex.get_pokemon_by_legendary(arg)

    def _get_by_type(self, arg):
        p_types = [a for a in arg.split(',') if a.strip()]
        if p_types:
            return self.pokedex.get_pokemon_by_type(p_types)

        return None

    def _get_by_stats(self, arg):
        stats = []
        for match in STATS_REGEX.finditer(arg):
            if not match:
                continue

            stats.append((match.group(1), match.group(2), int(match.group(3))))

        if stats:
            return self.pokedex.get_pokemon_by_stats(stats)

        return None

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
