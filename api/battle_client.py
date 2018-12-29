import pika
import time
import uuid
import json

class BattleClient(object):
    retries = 3

    def __init__(self, url, battle_queue):
        self.url = url
        self.battle_queue = battle_queue

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

        self.channel.basic_consume(self.on_battle_response, no_ack=True,
                                   queue=self.callback_queue)
        return self

    def __exit__(self, type, value, traceback):
        self.channel.close()
        self.connection.close()

    def send_request(self, data):
        self.response = None
        corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='', routing_key=self.battle_queue,
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=corr_id,
            ), body=json.dumps(data))

        while self.response is None:
            self.connection.process_data_events()

        return self.response

    def on_battle_response(self, ch, method, props, body):
        print("on_battle_response: {}".format(body))
        self.response = body
