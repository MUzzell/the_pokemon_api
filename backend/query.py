import pika
import os


def setup(channel):
    query_queue = os.getenv("QUERY_QUEUE")
    channel.queue_declare(queue=query_queue)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(handle_request, queue=query_queue)


def handle_request(ch, method, props, body):
    return