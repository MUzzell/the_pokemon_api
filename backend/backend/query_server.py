import pika


class QueryServer(object):

    def __init__(self, query_queue, pokedex):
        self.query_queue = query_queue
        self.pokedex = pokedex

    def setup(self, channel):
        channel.queue_declare(queue=self.query_queue)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(self.handle_request, queue=self.query_queue)

    def handle_request(self, ch, method, props, body):
        return
