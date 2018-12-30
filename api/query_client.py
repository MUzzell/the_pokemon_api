import pika
import time
import uuid
import json


def _format_query(q_type, data):
    return "{}:{}".format(q_type, data)


class QueryClient(object):
    retries = 3

    def __init__(self, url, query_queue):
        self.url = url
        self.query_queue = query_queue

    def __enter__(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(self.url)
            )
        except pika.exceptions.ConnectionClosed:
            if not self.retries:
                raise
            self.retries -= 1
            time.sleep(2)

        self.channel = self.connection.channel()
        result = self.channel.queue_declare(exclusive=True)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self._on_query_response, no_ack=True,
                                   queue=self.callback_queue)
        return self

    def __exit__(self, type, value, traceback):
        self.channel.close()
        self.connection.close()

    def get_by_id(self, ident):
        return self._send_request(_format_query("ID", ident))

    def get_by_name(self, name):
        return self._send_request(_format_query("NAME", name))

    def _send_request(self, message):
        self.response = None
        corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='', routing_key=self.query_queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=corr_id,
            ), body=message)

        while self.response is None:
            self.connection.process_data_events()

        return self.response

    def _on_query_response(self, ch, method, props, body):
        self.response = body.decode("ASCII")
