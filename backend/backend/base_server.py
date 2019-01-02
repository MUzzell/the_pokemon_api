import pika
import json


def parse_request(message):
    return message.decode('ASCII').split(":")


class BaseServer(object):

    def __init__(self, queue):
        self.queue_name = queue

    def handle_request(self, ch, method, props, body):
        try:
            args = parse_request(body)
            code, result = self._request_received(*args)
            self._send_result(ch, method, props, code, result)
        except Exception as e:
            raise
            self._send_result(ch, method, props, 500, "Server error")

    def _request_received(self, args):
        raise NotImplemented

    def setup(self, channel):
        channel.queue_declare(queue=self.queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.handle_request, queue=self.queue_name)

    def _send_result(self, ch, method, props, code, result):
        self._publish(ch, method, props,
                      {'code': code, 'data': result})

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
